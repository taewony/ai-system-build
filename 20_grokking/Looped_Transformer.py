import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. 하이퍼파라미터 설정 (Grokking에 최적화)
# ============================================================
P_MOD = 10                     # 10진수 연산
D_MODEL = 128                   # 임베딩 차원 (너무 크면 암기 쉬움)
NUM_HEADS = 4                   # 멀티헤드 어텐션 헤드 수
NUM_LOOPS = 6                   # 반복 계층 횟수 (LoopLM 스타일)

TRAIN_DIGITS = 4                # 학습할 최대 자릿수 (훈련 데이터에는 4자리 이하 + 일부 긴 예제)
TEST_DIGITS = 8                 # OOD 평가 자릿수

# ----- 데이터 구성 -----
TRAIN_SAMPLES = 2000             # ⭐ 훈련 샘플 수를 크게 줄임 (암기 방지)
VAL_SAMPLES = 500                # 검증 샘플 (in-distribution)
BRIDGE_RATIO = 0.15              # ⭐ 5~6자리 "브리지" 데이터 비율 (길이 일반화 도움)

BATCH_SIZE = 256                 # 배치 크기 (GPU 메모리에 맞게 조정)
LR = 1e-3                        # 초기 학습률
MIN_LR = 1e-4                    # 최소 학습률 (코사인 스케줄)
WD = 0.5                         # ⭐ 가중치 감쇠 대폭 증가 (암기 억제)
EPOCHS = 20000                   # ⭐ 충분히 긴 학습 (Grokking은 늦게 나타남)

CHARS = "0123456789+=$ "
CHAR_TO_IDX = {c: i for i, c in enumerate(CHARS)}
IDX_TO_CHAR = {i: c for i, c in enumerate(CHARS)}
VOCAB_SIZE = len(CHARS)

# ============================================================
# 2. 데이터 생성 함수 (LSB 우선 역순 + 브리지 데이터)
# ============================================================
def generate_number(digits, max_digits=None):
    """지정된 자릿수 이하의 무작위 정수 생성 (0 포함)"""
    if max_digits is None:
        max_digits = digits
    low = 0
    high = 10**digits
    return np.random.randint(low, high)

def format_pair(a, b, digits):
    """(a, b)를 역순 문자열로 변환 (예: 123 -> '321')"""
    q = f"{str(a)[::-1]:<{digits}}+{str(b)[::-1]:<{digits}}="
    res = a + b
    a_ans = f"{str(res)[::-1]:<{digits+1}}"  # 결과는 자릿수+1 (올림 고려)
    return q, a_ans

def generate_data(num_samples, max_digits, include_bridge=False):
    """
    max_digits 이하의 덧셈 데이터 생성.
    include_bridge=True이면 20%는 max_digits+1, max_digits+2 자릿수를 포함.
    """
    data = []
    bridge_digits = [max_digits + 1, max_digits + 2] if include_bridge else []
    for _ in range(num_samples):
        if include_bridge and np.random.random() < BRIDGE_RATIO:
            digits = np.random.choice(bridge_digits)
        else:
            digits = np.random.randint(1, max_digits + 1)  # 1~max_digits 자리
        a = generate_number(digits)
        b = generate_number(digits)
        q, a_ans = format_pair(a, b, digits)
        data.append((q, a_ans))
    return data

# ============================================================
# 3. Looped Transformer 모델 (RoPE + 반복 계층)
# ============================================================
class RoPE(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        inv_freq = 1.0 / (10000 ** (torch.arange(0, d_model, 2).float() / d_model))
        self.register_buffer("inv_freq", inv_freq)

    def forward(self, x):
        t = torch.arange(x.size(1), device=x.device).type_as(self.inv_freq)
        freqs = torch.einsum("i,j->ij", t, self.inv_freq)
        emb = torch.cat((freqs, freqs), dim=-1)
        # RoPE 회전 적용
        return x * emb.cos() + self._rotate_half(x) * emb.sin()

    def _rotate_half(self, x):
        x1, x2 = x.chunk(2, dim=-1)
        return torch.cat((-x2, x1), dim=-1)

class LoopedAdditionModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(VOCAB_SIZE, D_MODEL)
        self.rope = RoPE(D_MODEL)
        # 하나의 TransformerEncoderLayer를 여러 번 반복 (가중치 공유)
        self.layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL, nhead=NUM_HEADS, batch_first=True,
            norm_first=True, dropout=0.1   # ⭐ 소량의 드롭아웃 추가 (일반화)
        )
        self.output_head = nn.Linear(D_MODEL, VOCAB_SIZE)

    def forward(self, x):
        x = self.embed(x)
        x = self.rope(x)
        for _ in range(NUM_LOOPS):
            x = self.layer(x)
        return self.output_head(x)

# ============================================================
# 4. 학습 준비
# ============================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LoopedAdditionModel().to(device)
optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)

# 코사인 학습률 스케줄러 (Grokking에 유리)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=MIN_LR)

# 데이터 생성
train_raw = generate_data(TRAIN_SAMPLES, TRAIN_DIGITS, include_bridge=True)   # 브리지 포함
val_raw   = generate_data(VAL_SAMPLES, TRAIN_DIGITS, include_bridge=False)    # 검증은 순수 4자리 이하
ood_raw   = generate_data(20, TEST_DIGITS, include_bridge=False)              # OOD 테스트용

def encode_batch(data):
    """데이터 리스트를 텐서로 인코딩 (질문+정답을 하나의 시퀀스로)"""
    return torch.tensor([encode(q + a) for q, a in data]).to(device)

def decode(tokens):
    return "".join(IDX_TO_CHAR[t.item()] for t in tokens)

history = {"train_acc": [], "val_acc": []}

print(f"--- {TRAIN_DIGITS}자리 (브리지 포함) 학습 시작, OOD={TEST_DIGITS}자리 목표 ---")
print(f"훈련 샘플 수: {len(train_raw)}, 가중치 감쇠: {WD}")

# ============================================================
# 5. 학습 루프 (Grokking 모니터링)
# ============================================================
for epoch in range(EPOCHS):
    model.train()
    correct, total = 0, 0
    # 미니배치 학습
    for i in range(0, len(train_raw), BATCH_SIZE):
        batch = train_raw[i:i+BATCH_SIZE]
        x_enc = encode_batch(batch)  # (B, seq_len)

        optimizer.zero_grad()
        logits = model(x_enc[:, :-1])          # 입력: 마지막 토큰 제외
        loss = F.cross_entropy(
            logits.reshape(-1, VOCAB_SIZE),
            x_enc[:, 1:].reshape(-1)           # 타겟: 한 칸 시프트
        )
        loss.backward()
        optimizer.step()

        # 정확도 계산 (마지막 answer 부분만)
        preds = logits[:, -(TRAIN_DIGITS+1):].argmax(dim=-1)
        targets = x_enc[:, -(TRAIN_DIGITS+1):]
        correct += (preds == targets).all(dim=1).sum().item()
        total += len(batch)

    train_acc = correct / total

    # 검증 (in-distribution, 4자리 이하)
    model.eval()
    v_correct, v_total = 0, 0
    with torch.no_grad():
        for i in range(0, len(val_raw), BATCH_SIZE):
            batch = val_raw[i:i+BATCH_SIZE]
            x_enc = encode_batch(batch)
            logits = model(x_enc[:, :-1])
            preds = logits[:, -(TRAIN_DIGITS+1):].argmax(dim=-1)
            v_correct += (preds == x_enc[:, -(TRAIN_DIGITS+1):]).all(dim=1).sum().item()
            v_total += len(batch)
    val_acc = v_correct / v_total

    history["train_acc"].append(train_acc)
    history["val_acc"].append(val_acc)

    # 학습률 업데이트
    scheduler.step()

    if epoch % 200 == 0:
        current_lr = scheduler.get_last_lr()[0]
        print(f"Epoch {epoch:5d} | Train Acc {train_acc:.4f} | Val Acc {val_acc:.4f} | LR {current_lr:.2e}")
        if val_acc > 0.98:
            print(f"⭐ Grokking 발생! (Epoch {epoch})")
            # 멈추지 않고 계속 학습하여 일반화 강화

print("✅ 학습 완료")

# ============================================================
# 6. 최종 평가: In-distribution (4자리) vs OOD (8자리)
# ============================================================
def evaluate_model(data, title):
    print(f"\n[{title}]")
    model.eval()
    with torch.no_grad():
        for q, a_true in data:
            input_ids = encode(q)   # 질문만 인코딩
            # Greedy decoding
            for _ in range(len(a_true)):
                inp = torch.tensor([input_ids]).to(device)
                out = model(inp)
                next_token = out[0, -1].argmax().item()
                input_ids.append(next_token)

            res_str = decode(input_ids)
            pred_val = res_str.split('=')[1].strip()
            true_val = a_true.strip()
            status = "✅" if pred_val == true_val else "❌"
            print(f"Q: {q} | 예측: {pred_val} | 정답: {true_val} {status}")

# In-distribution 테스트 (4자리)
evaluate_model(generate_data(10, TRAIN_DIGITS, include_bridge=False), "In-Distribution (4-digit)")

# OOD 테스트 (8자리)
evaluate_model(generate_data(10, TEST_DIGITS, include_bridge=False), "OOD (8-digit)")

# ============================================================
# 7. Grokking 곡선 저장
# ============================================================
plt.figure(figsize=(10, 5))
plt.plot(history["train_acc"], label="Train Acc")
plt.plot(history["val_acc"], label="Val (4-digit) Acc")
plt.xlabel("Epoch")
plt.ylabel("Accuracy")
plt.title("Grokking on Addition (4→8 digits)")
plt.legend()
plt.grid(True)
plt.savefig("addition_grokking.pdf")
print("\n그래프 저장 완료: addition_grokking.pdf")
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
D_MODEL = 128                   # 임베딩 차원
NUM_HEADS = 4                   # 멀티헤드 어텐션 헤드 수
NUM_LOOPS = 6                   # 반복 계층 횟수

TRAIN_DIGITS = 4                # 학습할 최대 자릿수 (훈련 데이터에는 4자리 이하 + 일부 긴 예제)
TEST_DIGITS = 8                 # OOD 평가 자릿수

TRAIN_SAMPLES = 2000             # 훈련 샘플 수 (암기 방지를 위해 축소)
VAL_SAMPLES = 500                # 검증 샘플
BRIDGE_RATIO = 0.15              # 5~6자리 "브리지" 데이터 비율

BATCH_SIZE = 256                 # 배치 크기
LR = 1e-3                        # 초기 학습률
MIN_LR = 1e-4                    # 최소 학습률
WD = 0.5                         # 가중치 감쇠 (암기 억제)
EPOCHS = 20000                   # 충분히 긴 학습

CHARS = "0123456789+=$ "
CHAR_TO_IDX = {c: i for i, c in enumerate(CHARS)}
IDX_TO_CHAR = {i: c for i, c in enumerate(CHARS)}
VOCAB_SIZE = len(CHARS)

# ============================================================
# 2. 데이터 생성 함수 (LSB 우선 역순 + 브리지 데이터)
# ============================================================
def encode(text):
    """문자열을 인덱스 리스트로 변환"""
    return [CHAR_TO_IDX[c] for c in text]

def decode(tokens):
    """인덱스 리스트를 문자열로 변환"""
    return "".join(IDX_TO_CHAR[t] for t in tokens)

def generate_number(digits):
    """지정된 자릿수의 무작위 정수 생성 (0 포함)"""
    return np.random.randint(0, 10**digits)

def format_pair(a, b, digits):
    """
    (a, b)를 역순 문자열로 변환하고 정답도 함께 반환.
    반환: (질문_문자열, 정답_문자열, 정답_길이)
    """
    q = f"{str(a)[::-1]:<{digits}}+{str(b)[::-1]:<{digits}}="
    res = a + b
    # 정답은 자릿수+1 (올림 고려), 역순, 공백으로 오른쪽 패딩
    ans = f"{str(res)[::-1]:<{digits+1}}"
    return q, ans, len(ans)   # 정답 길이 저장

def generate_data(num_samples, max_digits, include_bridge=False):
    """
    max_digits 이하의 덧셈 데이터 생성.
    include_bridge=True이면 일부는 max_digits+1, max_digits+2 자릿수를 포함.
    반환: 리스트 [(질문_문자열, 정답_문자열, 정답_길이), ...]
    """
    data = []
    bridge_digits = [max_digits + 1, max_digits + 2] if include_bridge else []
    for _ in range(num_samples):
        if include_bridge and np.random.random() < BRIDGE_RATIO:
            digits = np.random.choice(bridge_digits)
        else:
            digits = np.random.randint(1, max_digits + 1)   # 1 ~ max_digits
        a = generate_number(digits)
        b = generate_number(digits)
        q, ans, ans_len = format_pair(a, b, digits)
        data.append((q, ans, ans_len))
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
            norm_first=True, dropout=0.1
        )
        self.output_head = nn.Linear(D_MODEL, VOCAB_SIZE)

    def forward(self, x):
        x = self.embed(x)
        x = self.rope(x)
        for _ in range(NUM_LOOPS):
            x = self.layer(x)
        return self.output_head(x)

# ============================================================
# 4. 배치 인코딩 (가변 길이 패딩)
# ============================================================
def encode_batch(data):
    """
    data: 리스트 [(q, ans, ans_len), ...]
    반환: (input_tensor, answer_lengths)
    - input_tensor: (B, max_seq_len) 패딩된 텐서
    - answer_lengths: 각 샘플의 정답 길이 (텐서)
    """
    sequences = [encode(q + ans) for q, ans, _ in data]
    answer_lengths = torch.tensor([l for _, _, l in data], device=device)
    max_len = max(len(seq) for seq in sequences)
    padded = torch.full((len(sequences), max_len), CHAR_TO_IDX[' '], dtype=torch.long)
    for i, seq in enumerate(sequences):
        padded[i, :len(seq)] = torch.tensor(seq, dtype=torch.long)
    return padded.to(device), answer_lengths

# ============================================================
# 5. 학습 준비
# ============================================================
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LoopedAdditionModel().to(device)
optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WD)
scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=EPOCHS, eta_min=MIN_LR)

# 데이터 생성
train_raw = generate_data(TRAIN_SAMPLES, TRAIN_DIGITS, include_bridge=True)
val_raw   = generate_data(VAL_SAMPLES, TRAIN_DIGITS, include_bridge=False)
ood_raw   = generate_data(20, TEST_DIGITS, include_bridge=False)

history = {"train_acc": [], "val_acc": []}
print(f"--- {TRAIN_DIGITS}자리 (브리지 포함) 학습 시작, OOD={TEST_DIGITS}자리 목표 ---")
print(f"훈련 샘플 수: {len(train_raw)}, 가중치 감쇠: {WD}")

# ============================================================
# 6. 학습 루프 (Grokking 모니터링)
# ============================================================
for epoch in range(EPOCHS):
    model.train()
    correct, total = 0, 0
    for i in range(0, len(train_raw), BATCH_SIZE):
        batch = train_raw[i:i+BATCH_SIZE]
        x_enc, ans_lens = encode_batch(batch)          # (B, T)

        optimizer.zero_grad()
        logits = model(x_enc[:, :-1])                  # (B, T-1, V)
        loss = F.cross_entropy(
            logits.reshape(-1, VOCAB_SIZE),
            x_enc[:, 1:].reshape(-1)                   # teacher forcing
        )
        loss.backward()
        optimizer.step()

        # 정확도 계산: 각 샘플의 정답 부분만 비교
        # 정답 시작 위치 = 전체 길이 - ans_len (마지막 ans_len 토큰)
        for j in range(len(batch)):
            seq_len = (x_enc[j] != CHAR_TO_IDX[' ']).sum().item()  # 실제 길이 (패딩 제외)
            ans_start = seq_len - ans_lens[j].item()
            pred_tokens = logits[j, ans_start-1:seq_len-1].argmax(dim=-1)  # -1 때문에 -1 보정
            true_tokens = x_enc[j, ans_start:seq_len]
            if torch.all(pred_tokens == true_tokens):
                correct += 1
        total += len(batch)

    train_acc = correct / total

    # 검증 (in-distribution)
    model.eval()
    v_correct, v_total = 0, 0
    with torch.no_grad():
        for i in range(0, len(val_raw), BATCH_SIZE):
            batch = val_raw[i:i+BATCH_SIZE]
            x_enc, ans_lens = encode_batch(batch)
            logits = model(x_enc[:, :-1])
            for j in range(len(batch)):
                seq_len = (x_enc[j] != CHAR_TO_IDX[' ']).sum().item()
                ans_start = seq_len - ans_lens[j].item()
                pred_tokens = logits[j, ans_start-1:seq_len-1].argmax(dim=-1)
                true_tokens = x_enc[j, ans_start:seq_len]
                if torch.all(pred_tokens == true_tokens):
                    v_correct += 1
            v_total += len(batch)
    val_acc = v_correct / v_total

    history["train_acc"].append(train_acc)
    history["val_acc"].append(val_acc)
    scheduler.step()

    if epoch % 200 == 0:
        current_lr = scheduler.get_last_lr()[0]
        print(f"Epoch {epoch:5d} | Train Acc {train_acc:.4f} | Val Acc {val_acc:.4f} | LR {current_lr:.2e}")
        if val_acc > 0.98:
            print(f"⭐ Grokking 발생! (Epoch {epoch})")

print("✅ 학습 완료")

# ============================================================
# 7. 최종 평가: In-distribution (4자리) vs OOD (8자리)
# ============================================================
def evaluate_model(data, title):
    print(f"\n[{title}]")
    model.eval()
    with torch.no_grad():
        for q, a_true, ans_len in data:
            input_ids = encode(q)               # 질문만 인코딩
            # Greedy decoding: 정답 길이만큼 생성
            generated = []
            for _ in range(ans_len):
                inp = torch.tensor([input_ids + generated]).to(device)
                out = model(inp)
                next_token = out[0, -1].argmax().item()
                generated.append(next_token)
            pred_str = decode(generated).strip()
            true_str = a_true.strip()
            status = "✅" if pred_str == true_str else "❌"
            print(f"Q: {q} | 예측: {pred_str} | 정답: {true_str} {status}")

evaluate_model(generate_data(10, TRAIN_DIGITS, include_bridge=False), "In-Distribution (4-digit)")
evaluate_model(generate_data(10, TEST_DIGITS, include_bridge=False), "OOD (8-digit)")

# ============================================================
# 8. Grokking 곡선 저장
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
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt

# 1. 하이퍼파라미터 설정 (Grokking의 핵심은 Weight Decay와 소수 P)
P = 97  # 소수(Prime) 사용
TRAIN_PCT = 0.3  # 30%만 학습 데이터로 사용 (나머지는 OOD/Validation)
D_MODEL = 128
NUM_HEADS = 4
NUM_LAYERS = 2
BATCH_SIZE = 512
LR = 1e-3
WD = 1.0  # 강한 Weight Decay가 깨달음(Grokking)을 유도함

# 2. 데이터셋 생성 (a + b = c mod P)
pairs = torch.cartesian_prod(torch.arange(P), torch.arange(P))
x = pairs
y = (pairs[:, 0] + pairs[:, 1]) % P

# 데이터 셔플 및 분할
indices = torch.randperm(P * P)
train_idx = indices[:int(len(indices) * TRAIN_PCT)]
val_idx = indices[int(len(indices) * TRAIN_PCT):]

train_loader = DataLoader(TensorDataset(x[train_idx], y[train_idx]), batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(TensorDataset(x[val_idx], y[val_idx]), batch_size=BATCH_SIZE)

# 3. 간단한 Transformer 모델 (Decoder-only)
class GrokTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(P, D_MODEL)
        self.pos_embed = nn.Parameter(torch.randn(2, D_MODEL)) # a, b 두 자리
        encoder_layer = nn.TransformerEncoderLayer(d_model=D_MODEL, nhead=NUM_HEADS, 
                                                   dim_feedforward=D_MODEL*4, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=NUM_LAYERS)
        self.fc = nn.Linear(D_MODEL, P)

    def forward(self, x):
        # x shape: (batch, 2)
        x = self.embed(x) + self.pos_embed
        x = self.transformer(x)
        x = x[:, -1, :] # 마지막 토큰의 결과 사용
        return self.fc(x)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = GrokTransformer().to(device)
optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WD, betas=(0.9, 0.98))
criterion = nn.CrossEntropyLoss()

# 4. 학습 루프 및 기록
history = {"train_acc": [], "val_acc": []}

for epoch in range(10000): # 깨달음이 올 때까지 충분히 반복
    model.train()
    correct, total = 0, 0
    for batch_x, batch_y in train_loader:
        batch_x, batch_y = batch_x.to(device), batch_y.to(device)
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        correct += (outputs.argmax(1) == batch_y).sum().item()
        total += batch_y.size(0)
    
    train_acc = correct / total
    
    # Validation (OOD 체크)
    model.eval()
    val_correct, val_total = 0, 0
    with torch.no_grad():
        for batch_x, batch_y in val_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            outputs = model(batch_x)
            val_correct += (outputs.argmax(1) == batch_y).sum().item()
            val_total += batch_y.size(0)
    
    val_acc = val_correct / val_total
    history["train_acc"].append(train_acc)
    history["val_acc"].append(val_acc)

    if epoch % 100 == 0:
        print(f"Epoch {epoch}: Train {train_acc:.2f}, Val {val_acc:.2f}")
    
    if val_acc > 0.99: # 깨달음 도달 시 종료
        print("Grokking Achieved!")
        break

# 결과 시각화
# 1. 결과 시각화 및 PDF 저장
plt.figure(figsize=(10, 5))
plt.plot(history["train_acc"], label="Train Accuracy (Memorization)", color='blue', alpha=0.7)
plt.plot(history["val_acc"], label="Validation Accuracy (Generalization/Grokking)", color='red', linewidth=2)
plt.axhline(y=1.0, color='gray', linestyle='--', alpha=0.5)
plt.title(f"Grokking on Modular Addition (P={P})")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.grid(True, alpha=0.3)

# PDF 파일로 저장 (remote 환경에서 확인 용이)
plt.savefig("grokking_result.pdf")
print("\n[알림] 학습 결과 그래프가 'grokking_result.pdf'로 저장되었습니다.")

# 2. OOD(Out-of-Distribution) 테스트 세션
print("\n" + "="*30)
print("   OOD 직접 테스트 (모델의 깨달음 검증)")
print("="*30)

model.eval()
with torch.no_grad():
    # 학습에 쓰이지 않은 샘플 5개 무작위 추출
    test_samples = val_idx[:5] 
    
    for idx in test_samples:
        a_val, b_val = x[idx]
        correct_ans = y[idx].item()
        
        # 모델 예측
        input_tensor = x[idx].unsqueeze(0).to(device) # (1, 2)
        output = model(input_tensor)
        pred_ans = output.argmax(1).item()
        
        status = "✅ 정답!" if pred_ans == correct_ans else "❌ 오답"
        print(f"입력: {a_val.item()} + {b_val.item()} (mod {P})")
        print(f"  - 실제 정답: {correct_ans}")
        print(f"  - 모델 예측: {pred_ans} [{status}]")
        print("-" * 20)

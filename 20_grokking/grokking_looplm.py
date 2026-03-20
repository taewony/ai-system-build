import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. 하이퍼파라미터 설정
# ---------------------------------------------------------
P = 97            # 소수 모듈러
TRAIN_PCT = 0.3   # 30% 학습, 70% OOD (난이도 상향)
D_MODEL = 128
NUM_HEADS = 4
NUM_LOOPS = 4     # [Semantic Layer] 에이전트가 결정할 반복 횟수 (Latent Reasoning)
BATCH_SIZE = 512
LR = 1e-3
WD = 1.0          # Grokking 유도를 위한 강한 가중치 감쇄

# ---------------------------------------------------------
# 2. 데이터셋 생성 (a + b = c mod P)
# ---------------------------------------------------------
pairs = torch.cartesian_prod(torch.arange(P), torch.arange(P))
x = pairs
y = (pairs[:, 0] + pairs[:, 1]) % P

indices = torch.randperm(P * P)
train_idx = indices[:int(len(indices) * TRAIN_PCT)]
val_idx = indices[int(len(indices) * TRAIN_PCT):]

train_loader = DataLoader(TensorDataset(x[train_idx], y[train_idx]), batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(TensorDataset(x[val_idx], y[val_idx]), batch_size=BATCH_SIZE)

# ---------------------------------------------------------
# 3. Looped Transformer 모델 (Looped LLM)
# ---------------------------------------------------------
class LoopedGrokTransformer(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(P, D_MODEL)
        self.pos_embed = nn.Parameter(torch.randn(2, D_MODEL))
        
        # 단일 레이어 정의 (이 가중치가 반복 사용됨 -> Kernel 계층에서 최적화 대상)
        self.layer = nn.TransformerEncoderLayer(
            d_model=D_MODEL, 
            nhead=NUM_HEADS, 
            dim_feedforward=D_MODEL*4, 
            batch_first=True,
            norm_first=True # 안정적인 반복 학습을 위해 선호됨
        )
        self.fc = nn.Linear(D_MODEL, P)

    def forward(self, x):
        # x shape: (batch, 2)
        x = self.embed(x) + self.pos_embed
        
        # [Semantic/Agent Layer] 명세에 따른 반복 추론 (Latent Reasoning)
        for _ in range(NUM_LOOPS):
            x = self.layer(x)
            
        x = x[:, -1, :] # 마지막 토큰의 결과 사용
        return self.fc(x)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LoopedGrokTransformer().to(device)
optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WD, betas=(0.9, 0.98))
criterion = nn.CrossEntropyLoss()

# ---------------------------------------------------------
# 4. 학습 루프
# ---------------------------------------------------------
history = {"train_acc": [], "val_acc": []}

print(f"학습 시작 (Device: {device}, Loops: {NUM_LOOPS})...")

for epoch in range(15000): # Looped 모델은 깨달음에 조금 더 많은 시간이 걸릴 수 있음
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
        print(f"Epoch {epoch}: Train Acc {train_acc:.4f}, Val(OOD) Acc {val_acc:.4f}")
    
    if val_acc > 0.98: 
        print(f"Grokking Achieved at Epoch {epoch}!")
        break

# ---------------------------------------------------------
# 5. 결과 시각화 및 OOD 테스트
# ---------------------------------------------------------
plt.figure(figsize=(12, 6))
plt.plot(history["train_acc"], label="Train (Memorization)", color='blue', alpha=0.6)
plt.plot(history["val_acc"], label="Validation (Generalization/Grokking)", color='red', linewidth=2)
plt.title(f"Looped LLM Grokking (Loops={NUM_LOOPS}, P={P})")
plt.xlabel("Epochs")
plt.ylabel("Accuracy")
plt.legend()
plt.grid(True, alpha=0.3)
plt.savefig("looped_grokking_result.pdf")

print("\n" + "="*40)
print("   OOD(학습 시 보지 못한 데이터) 직접 테스트")
print("="*40)

model.eval()
with torch.no_grad():
    test_indices = val_idx[:5] 
    for idx in test_indices:
        a, b = x[idx]
        actual = y[idx].item()
        pred = model(x[idx].unsqueeze(0).to(device)).argmax(1).item()
        print(f"입력: {a.item()} + {b.item()} (mod {P}) -> 정답: {actual}, 예측: {pred} [{'OK' if actual==pred else 'FAIL'}]")

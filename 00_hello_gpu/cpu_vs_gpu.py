import torch
import time
import matplotlib.pyplot as plt

def measure_cpu_time(size, repeat=30):
    times = []
    for _ in range(repeat):
        a = torch.randn(size, size)
        b = torch.randn(size, size)
        start = time.time()
        torch.matmul(a, b)
        end = time.time()
        times.append(end - start)
    return sum(times) / repeat

def measure_gpu_time(size, repeat=30):
    if not torch.cuda.is_available():
        return None
    
    # 워밍업
    a = torch.randn(size, size, device='cuda')
    b = torch.randn(size, size, device='cuda')
    torch.matmul(a, b)
    torch.cuda.synchronize()

    times = []
    for _ in range(repeat):
        a = torch.randn(size, size, device='cuda')
        b = torch.randn(size, size, device='cuda')
        start = time.time()
        torch.matmul(a, b)
        torch.cuda.synchronize()  # GPU 연산 완료 대기
        end = time.time()
        times.append(end - start)
    return sum(times) / repeat

# 설정 및 측정
sizes = [100, 200, 400, 800, 1600]
print(f"{'Size':>6} | {'CPU (s)':>10} | {'GPU (s)':>10} | {'Speedup':>8}")
print("-" * 45)

cpu_times = []
gpu_times = []

for size in sizes:
    c_time = measure_cpu_time(size)
    g_time = measure_gpu_time(size)
    
    cpu_times.append(c_time)
    gpu_times.append(g_time)
    
    if g_time:
        speedup = c_time / g_time
        print(f"{size:6d} | {c_time:10.6f} | {g_time:10.6f} | {speedup:7.2f}x")
    else:
        print(f"{size:6d} | {c_time:10.6f} | {'N/A':>10} | {'N/A':>8}")

# --- 결과 시각화 및 파일 저장 ---
plt.figure(figsize=(10, 6))
plt.plot(sizes, cpu_times, marker='o', label='CPU')
if any(gpu_times):
    plt.plot(sizes, gpu_times, marker='s', label='GPU')

plt.title('Matrix Multiplication Performance: CPU vs GPU')
plt.xlabel('Matrix Size (N x N)')
plt.ylabel('Average Time (sec)')
plt.legend()
plt.grid(True)

# 파일로 저장 (VS Code 탐색기에서 바로 볼 수 있음)
plt.savefig('performance_result.png')
print("\n[알림] 그래프가 'performance_result.png'로 저장되었습니다.")
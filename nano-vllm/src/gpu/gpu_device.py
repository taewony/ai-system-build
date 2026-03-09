import torch

if not torch.cuda.is_available():
    print("CUDA is NOT available.")
    exit()

props = torch.cuda.get_device_properties(0)

print(f"===== Device 0 Information =====")
print(f"Name: {props.name}")
print(f"Compute Capability: {props.major}.{props.minor}")
print(f"MultiProcessor Count: {props.multi_processor_count}")

# 속성명이 다를 수 있으므로 getattr로 안전하게 가져옵니다.
# PyTorch 버전에 따라 'total_shared_mem' 또는 'shared_mem_per_block'일 수 있습니다.
shared_mem = getattr(props, 'total_shared_mem', "N/A")
max_threads = getattr(props, 'max_threads_per_block', "N/A")
warp_size = getattr(props, 'warp_size', "N/A")

if isinstance(shared_mem, int):
    print(f"Shared Memory per Block: {shared_mem / 1024:.2f} KB")
else:
    print(f"Shared Memory: {shared_mem}")

print(f"Max Threads per Block: {max_threads}")
print(f"Warp Size: {warp_size}")
print(f"Total Global Memory: {props.total_memory / (1024**3):.2f} GB")
print("================================")
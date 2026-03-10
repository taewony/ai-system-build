import torch

props = torch.cuda.get_device_properties(0)

print(f"===== Device 0 Information (Verified) =====")
print(f"Name: {props.name}")
print(f"Compute Capability: {props.major}.{props.minor}")
print(f"MultiProcessor Count (SM): {props.multi_processor_count}")
print(f"Warp Size: {props.warp_size}")
print(f"Total Memory: {props.total_memory / (1024**3):.2f} GB")

# 확인된 리스트에 있는 속성들
print(f"L2 Cache Size: {props.L2_cache_size / 1024 / 1024:.2f} MB")
print(f"Max Threads per SM: {props.max_threads_per_multi_processor}")
print(f"Regs per SM: {props.regs_per_multiprocessor}")
print(f"Architecture Name: {getattr(props, 'gcnArchName', 'N/A')}")
print(f"UUID: {props.uuid}")
print("===========================================")
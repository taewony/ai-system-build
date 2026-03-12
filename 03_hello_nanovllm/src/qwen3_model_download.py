from huggingface_hub import snapshot_download

# Hugging Face repository
repo_id = "Qwen/Qwen3-8B"

# Local directory where the model will be stored
local_dir = "./models/Qwen3-8B"

# Download the full repository snapshot
snapshot_download(
    repo_id=repo_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False,   # safer for container / nano-vllm
    revision="main"
)

print(f"Model downloaded to: {local_dir}")
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="Qwen/Qwen3-8B",
    local_dir="/home/jovyan/shared-data/models/huggingface/Qwen3-8B"
)

print("Download complete")
import os
import argparse
import json
from transformers import AutoConfig

def human_readable_size(num_bytes):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.2f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.2f} PB"

def inspect_vllm_metadata(model_path):

    if not os.path.exists(model_path):
        print(f"❌ Error: {model_path} 경로를 찾을 수 없습니다.")
        return

    print("\n🔎 Qwen / vLLM Model Inspector")
    print("=" * 70)

    config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)

    arch = getattr(config, "architectures", ["Unknown"])[0]
    hidden_size = getattr(config, "hidden_size", 0)
    num_heads = getattr(config, "num_attention_heads", 0)
    num_kv_heads = getattr(config, "num_key_value_heads", num_heads)
    num_layers = getattr(config, "num_hidden_layers", 0)
    vocab_size = getattr(config, "vocab_size", 0)

    head_dim = hidden_size // num_heads if num_heads else 0

    max_pos = getattr(config, "max_position_embeddings", 0)

    rope_theta = getattr(config, "rope_theta", None)

    intermediate = getattr(config, "intermediate_size", None)

    print("\n🏗️ Transformer Architecture")
    print("-" * 70)

    print(f"Architecture           : {arch}")
    print(f"Hidden Size            : {hidden_size}")
    print(f"Layers                 : {num_layers}")
    print(f"Attention Heads        : {num_heads}")
    print(f"KV Heads (GQA)         : {num_kv_heads}")
    print(f"Head Dimension         : {head_dim}")

    if num_kv_heads:
        print(f"GQA Ratio              : {num_heads // num_kv_heads}:1")

    print(f"FFN Intermediate Size  : {intermediate}")
    print(f"Vocabulary Size        : {vocab_size}")
    print(f"Max Position Embedding : {max_pos}")

    if rope_theta:
        print(f"RoPE Theta             : {rope_theta}")

    print("\n🧠 Transformer Block Interpretation")
    print("-" * 70)

    print("Each transformer layer consists of:")
    print(" 1. Multi-Head Attention")
    print(" 2. Feed Forward Network")
    print(" 3. LayerNorm")

    print("\nAttention structure:")
    print(f"  Q heads : {num_heads}")
    print(f"  KV heads: {num_kv_heads}")
    print("  → Grouped Query Attention (GQA) used")

    if intermediate:
        print("\nFFN structure (approx):")
        print(f"  Hidden → {intermediate} → Hidden")

    print("\n📊 Parameter Estimation")
    print("-" * 70)

    if intermediate:

        attn_params = (
            hidden_size * hidden_size * 3
            + hidden_size * hidden_size
        )

        ffn_params = (
            hidden_size * intermediate
            + intermediate * hidden_size
        )

        layer_params = attn_params + ffn_params

        total_params = layer_params * num_layers

        embedding_params = vocab_size * hidden_size

        total_params += embedding_params

        print(f"Estimated parameters : {total_params/1e9:.2f} B")

        weight_memory = total_params * 2

        print(f"Weight memory (FP16) : {human_readable_size(weight_memory)}")

    print("\n🚀 KV Cache Analysis (vLLM)")
    print("-" * 70)

    block_size = 16

    bytes_per_token = 2 * 2 * num_layers * num_kv_heads * head_dim

    print(f"KV cache per token : {human_readable_size(bytes_per_token)}")

    block_mem = bytes_per_token * block_size

    print(f"KV cache per block ({block_size}) : {human_readable_size(block_mem)}")

    print("\n📦 Context Memory Examples")

    for seq in [1024, 4096, 8192, 32768]:

        mem = seq * bytes_per_token
        print(f"{seq:6d} tokens → {human_readable_size(mem)}")

    print("\n⚡ Tensor Parallel Feasibility")
    print("-" * 70)

    for tp in [2, 4, 8]:

        if num_heads % tp == 0:

            print(
                f"TP={tp} → OK "
                f"(heads/GPU={num_heads//tp}, kv_heads/GPU={num_kv_heads//tp})"
            )

        else:

            print(f"TP={tp} → ⚠️ head mismatch")

    print("\n🧬 Qwen Model Characteristics")
    print("-" * 70)

    print("Model family : Alibaba Qwen LLM")
    print("Architecture : Decoder-only Transformer")
    print("Attention    : Grouped Query Attention (memory efficient)")
    print("Position     : RoPE positional embedding")
    print("Tokenizer    : BPE based tokenizer")

    if rope_theta:
        print("Long context : Enabled via RoPE scaling")

    print("\n📂 Raw Config Fields")
    print("-" * 70)

    raw = config.to_dict()

    important = [
        "hidden_size",
        "num_attention_heads",
        "num_key_value_heads",
        "num_hidden_layers",
        "intermediate_size",
        "rope_theta",
        "max_position_embeddings",
        "torch_dtype",
        "tie_word_embeddings",
    ]

    for k in important:
        if k in raw:
            print(f"{k:30s}: {raw[k]}")

    print("\n✅ Analysis complete\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "model_path",
        nargs="?",                      # argument optional
        default="./models/huggingface/Qwen3-8B",    # default path
        help="HuggingFace model path (default: ./models/huggingface/Qwen3-8B)"
    )

    args = parser.parse_args()

    inspect_vllm_metadata(args.model_path)
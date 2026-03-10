import os
import time
import random
from dataclasses import dataclass
from transformers import AutoConfig


DEFAULT_MODEL_PATH = "./models/Qwen3-8B"


# ------------------------------------------------
# Model Metadata
# ------------------------------------------------

@dataclass
class ModelMeta:

    hidden_size: int
    num_layers: int
    num_heads: int
    num_kv_heads: int
    vocab_size: int
    max_position: int
    head_dim: int
    kv_cache_bytes_per_token: int


def load_model_meta(model_path):

    config = AutoConfig.from_pretrained(model_path, trust_remote_code=True)

    hidden = config.hidden_size
    layers = config.num_hidden_layers
    heads = config.num_attention_heads
    kv_heads = getattr(config, "num_key_value_heads", heads)
    vocab = config.vocab_size
    max_pos = config.max_position_embeddings

    head_dim = hidden // heads

    kv_bytes = 2 * 2 * layers * kv_heads * head_dim

    meta = ModelMeta(
        hidden,
        layers,
        heads,
        kv_heads,
        vocab,
        max_pos,
        head_dim,
        kv_bytes
    )

    return meta


# ------------------------------------------------
# Sequence
# ------------------------------------------------

class Sequence:

    _id_counter = 0

    def __init__(self, prompt_tokens, max_tokens=32):

        Sequence._id_counter += 1
        self.seq_id = Sequence._id_counter

        self.token_ids = list(prompt_tokens)
        self.prompt_len = len(prompt_tokens)

        self.generated = 0
        self.max_tokens = max_tokens

        self.block_table = []
        self.finished = False

    def append(self, token):

        self.token_ids.append(token)
        self.generated += 1

        if self.generated >= self.max_tokens:
            self.finished = True

    def __len__(self):

        return len(self.token_ids)


# ------------------------------------------------
# KV Cache Block Manager
# ------------------------------------------------

class KVCacheManager:

    def __init__(self, total_blocks):

        self.free_blocks = list(range(total_blocks))
        self.used_blocks = {}

    def allocate(self, seq_id):

        if not self.free_blocks:
            raise RuntimeError("Out of KV cache blocks")

        block = self.free_blocks.pop()
        self.used_blocks.setdefault(seq_id, []).append(block)

        return block

    def free(self, seq_id):

        blocks = self.used_blocks.get(seq_id, [])

        for b in blocks:
            self.free_blocks.append(b)

        self.used_blocks.pop(seq_id, None)


# ------------------------------------------------
# Scheduler
# ------------------------------------------------

class Scheduler:

    def __init__(self, meta, num_blocks=200, block_size=16):

        self.meta = meta
        self.block_size = block_size

        self.block_manager = KVCacheManager(num_blocks)

        self.waiting = []
        self.running = []

    def add(self, seq):

        self.waiting.append(seq)

    def schedule(self):

        scheduled = []

        if self.waiting:

            seq = self.waiting.pop(0)

            blocks_needed = (len(seq) + self.block_size - 1) // self.block_size

            for _ in range(blocks_needed):
                block = self.block_manager.allocate(seq.seq_id)
                seq.block_table.append(block)

            self.running.append(seq)

            scheduled.append(seq)

            return scheduled, True

        for seq in self.running:

            if not seq.finished:
                scheduled.append(seq)

        return scheduled, False

    def postprocess(self, seqs, token_ids):

        for seq, tok in zip(seqs, token_ids):

            seq.append(tok)

            if len(seq) % self.block_size == 0:
                block = self.block_manager.allocate(seq.seq_id)
                seq.block_table.append(block)

        for seq in list(self.running):

            if seq.finished:

                self.block_manager.free(seq.seq_id)
                self.running.remove(seq)

    def is_finished(self):

        return not self.waiting and not self.running


# ------------------------------------------------
# Mock GPU Model Runner
# ------------------------------------------------

class MockModelRunner:

    def __init__(self, vocab_size):

        self.vocab_size = vocab_size

    def run(self, seqs, is_prefill):

        if is_prefill:

            tokens = sum(len(s) for s in seqs)
            time.sleep(min(0.05, tokens * 0.0001))

        else:

            time.sleep(0.003)

        outputs = []

        for seq in seqs:

            next_token = (seq.token_ids[-1] + 1) % self.vocab_size
            outputs.append(next_token)

        return outputs


# ------------------------------------------------
# Simulation
# ------------------------------------------------

def run_simulation(model_path):

    print("\n🚀 CPU vLLM Simulation\n")

    meta = load_model_meta(model_path)

    print("Model loaded")
    print(f"hidden={meta.hidden_size}")
    print(f"layers={meta.num_layers}")
    print(f"heads={meta.num_heads}")
    print(f"kv_heads={meta.num_kv_heads}")
    print(f"vocab={meta.vocab_size}")
    print()

    scheduler = Scheduler(meta, num_blocks=120)

    runner = MockModelRunner(meta.vocab_size)

    prompts = [
        [1,2,3,4,5,6,7,8],
        [10,11,12,13]
    ]

    for p in prompts:

        seq = Sequence(p)
        scheduler.add(seq)

        print(f"request added seq={seq.seq_id} prompt={len(p)}")

    step = 0

    while not scheduler.is_finished():

        step += 1
        print(f"\n--- step {step} ---")

        seqs, prefill = scheduler.schedule()

        if not seqs:
            continue

        mode = "prefill" if prefill else "decode"

        tokens = runner.run(seqs, prefill)

        scheduler.postprocess(seqs, tokens)

        for s in seqs:

            print(
                f"{mode} seq={s.seq_id} "
                f"tokens={len(s)} "
                f"blocks={len(s.block_table)} "
                f"finished={s.finished}"
            )

        free_blocks = len(scheduler.block_manager.free_blocks)

        print(f"free blocks={free_blocks}")

    print("\n✅ simulation finished")


# ------------------------------------------------


if __name__ == "__main__":

    model_path = os.getenv("MODEL_PATH", DEFAULT_MODEL_PATH)

    run_simulation(model_path)
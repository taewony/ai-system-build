import os
from nanovllm import LLM, SamplingParams
from transformers import AutoTokenizer
from pathlib import Path  # 이 라인이 반드시 필요합니다.

def main():
    # 상대 경로를 절대 경로로 변환
    model_path = Path("/home/jovyan/shared-data/models/huggingface/Qwen3-8B").resolve()
    if not (model_path / "config.json").exists():
        print(f"❌ 모델 파일을 찾을 수 없습니다: {model_path}")
        return

    # 2. 토크나이저 로드 (안정성을 위해 try-except 권장)
    try:
        # 먼저 로컬 경로 시도
        tokenizer = AutoTokenizer.from_pretrained(str(model_path), trust_remote_code=True)
    except Exception:
        print(f"⚠️ 로컬 토크나이저 로드 실패: {e}")
        return

    # 3. LLM 초기화 (L40S GPU 최적화)
    llm = LLM(
        model=str(model_path),
        enforce_eager=True, 
        tensor_parallel_size=1,
        dtype="bfloat16" # L40S(Ada) 아키텍처는 BF16에서 최대 성능을 냅니다.
    )

    sampling_params = SamplingParams(temperature=0.6, max_tokens=256)
    prompts = [
        "introduce yourself",
        "list all prime numbers within 100",
    ]
    prompts = [
        tokenizer.apply_chat_template(
            [{"role": "user", "content": prompt}],
            tokenize=False,
            add_generation_prompt=True,
        )
        for prompt in prompts
    ]
    outputs = llm.generate(prompts, sampling_params)

    for prompt, output in zip(prompts, outputs):
        print("\n")
        print(f"Prompt: {prompt!r}")
        print(f"Completion: {output['text']!r}")


if __name__ == "__main__":
    main()

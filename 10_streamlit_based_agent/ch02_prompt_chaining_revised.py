import ollama
from typing import List

# ============================================
# 1. LLM 호출 함수 (Ollama 사용)
# ============================================
def llm_call(prompt: str, model: str = "qwen3:8b") -> str:
    """
    Ollama를 사용하여 프롬프트를 전송하고 응답을 반환합니다.
    """
    response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
    return response["message"]["content"].strip()


# ============================================
# 2. 프롬프트 체이닝 워크플로우
# ============================================
def prompt_chain_workflow(initial_input: str, prompt_chain: List[str]) -> List[str]:
    """
    여러 단계의 프롬프트를 순차적으로 실행하며, 이전 응답을 다음 단계에 전달합니다.
    
    Args:
        initial_input: 사용자의 첫 입력 (첫 단계에서만 사용됨)
        prompt_chain: 각 단계의 프롬프트 템플릿 리스트
    
    Returns:
        각 단계의 응답을 담은 리스트
    """
    responses = []
    current_context = initial_input  # 첫 단계에서는 사용자 입력을 컨텍스트로 사용

    for i, prompt_template in enumerate(prompt_chain, 1):
        print(f"\n--- {i}단계 진행 중 ---")

        # 현재 단계에 맞는 프롬프트 생성
        # - 첫 단계: initial_input을 포함
        # - 이후 단계: 이전 응답을 포함
        if i == 1:
            final_prompt = f"{prompt_template}\n\n사용자 입력:\n{initial_input}"
        else:
            final_prompt = f"{prompt_template}\n\n이전 단계 응답:\n{current_context}"

        # LLM 호출
        response = llm_call(final_prompt)
        responses.append(response)

        # 다음 단계를 위해 현재 응답을 컨텍스트로 저장
        current_context = response

        print(f"✅ 응답 받음 (길이: {len(response)}자)\n")
        print(response)

    return responses


# ============================================
# 3. 실행 (메인)
# ============================================
if __name__ == "__main__":
    # 단계별 프롬프트 템플릿 (각 단계의 역할이 명확히 드러나도록 간결하게 작성)
    prompts = [
        # 1단계: 후보 추천
        """사용자의 여행 취향을 분석하여 적합한 여행지 세 곳을 추천하세요.
- 사용자 취향 요약
- 추천 이유
- 각 여행지의 기후와 주요 관광지""",

        # 2단계: 최종 선택 및 활동 제안
        """위 추천 중 가장 적합한 여행지 한 곳을 선정하고, 그곳에서 할 수 있는 다섯 가지 활동을 제안하세요.
- 선정 이유
- 자연, 역사, 음식 등 다양한 분야의 활동""",

        # 3단계: 하루 일정 계획
        """선정된 여행지의 하루 일정을 오전/오후/저녁으로 나누어 계획하세요.
- 시간대별 활동
- 이동 및 소요 시간 고려"""
    ]

    # 사용자 입력
    user_input = input("여행 스타일을 입력하세요 (예: 따뜻한 날씨, 역사적인 장소 선호):\n> ")

    # 프롬프트 체이닝 실행
    results = prompt_chain_workflow(user_input, prompts)

    # 최종 결과 출력
    print("\n========== 최종 일정 ==========")
    print(results[-1])
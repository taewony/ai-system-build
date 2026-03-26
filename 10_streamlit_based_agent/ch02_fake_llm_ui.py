import streamlit as st
from typing import List

# ============================================
# Fake LLM Call (UI 테스트용)
# ============================================
def fake_llm_call(prompt: str) -> str:
    """
    실제 LLM 호출을 대체하는 가짜 함수.
    프롬프트 내용에 따라 미리 준비된 더미 응답을 반환합니다.
    """
    if "세 곳을 추천" in prompt:
        return (
            "사용자는 따뜻한 날씨와 자연/역사적 장소를 선호합니다.\n\n"
            "1. **제주도**\n"
            "   - 추천 이유: 온화한 기후, 한라산(자연)과 성산일출봉(역사/문화)이 조화를 이룸.\n"
            "   - 기후: 연중 온난, 봄/가을 특히 쾌적.\n"
            "   - 주요 관광지: 한라산, 성산일출봉, 만장굴, 오설록 녹차밭.\n\n"
            "2. **경주**\n"
            "   - 추천 이유: 역사적 장소가 풍부하고 봄/가을 날씨가 쾌적함.\n"
            "   - 기후: 봄/가을 맑고 선선함.\n"
            "   - 주요 관광지: 불국사, 석굴암, 첨성대, 동궁과 월지.\n\n"
            "3. **강릉**\n"
            "   - 추천 이유: 바다와 산(자연) 그리고 역사적 유적(오죽헌)을 함께 즐길 수 있음.\n"
            "   - 기후: 여름에는 시원하고 겨울에는 눈이 내려 아름다움.\n"
            "   - 주요 관광지: 경포대, 오죽헌, 안목해변, 커피거리."
        )
    elif "활동을 제안" in prompt:
        return (
            "가장 추천하는 여행지는 **제주도**입니다.\n\n"
            "선정 이유: 자연(한라산, 오름)과 역사(성산일출봉, 제주 민속문화)를 모두 경험할 수 있으며, "
            "사용자가 선호하는 따뜻한 날씨에 가장 적합합니다.\n\n"
            "다섯 가지 활동:\n"
            "1. **자연 탐방**: 한라산 등반 (국립공원)\n"
            "2. **역사 탐방**: 성산일출봉 일출 감상 (세계자연유산)\n"
            "3. **자연 탐방**: 제주 오름 트레킹 (예: 사려니오름)\n"
            "4. **음식 체험**: 해녀 체험 및 해산물 요리\n"
            "5. **문화 체험**: 유채꽃밭 산책 (봄철) / 감귤 따기 체험 (가을)"
        )
    elif "하루 일정 계획" in prompt:
        return (
            "**제주도 하루 일정 (자연 & 역사 중심)**\n\n"
            "☀️ **오전**\n"
            "- 07:00 ~ 09:00: 성산일출봉 일출 감상 및 등반 (역사/자연)\n"
            "- 09:00 ~ 11:00: 우도(牛島)로 이동, 섬 일주 및 해녀 체험 (음식/문화)\n\n"
            "☁️ **오후**\n"
            "- 11:00 ~ 13:00: 점심 (우도 땅콩 아이스크림, 해물 라면)\n"
            "- 13:00 ~ 16:00: 만장굴 용암동굴 탐험 (자연)\n"
            "- 16:00 ~ 18:00: 제주 민속촌 방문 (역사/문화)\n\n"
            "🌙 **저녁**\n"
            "- 18:00 ~ 20:00: 제주 흑돼지 BBQ (음식 체험)\n"
            "- 20:00 ~ : 해안가 산책 및 휴식"
        )
    else:
        return f"[테스트 응답] 다음 프롬프트에 대한 가상 응답입니다:\n{prompt[:200]}..."

# ============================================
# 기본 프롬프트 (원본 유지)
# ============================================
default_prompts = [
    """사용자의 여행 취향을 바탕으로 적합한 여행지 세 곳을 추천해.
- 사용자가 입력한 내용을 요약해.
- 추천한 여행지가 왜 적합한지 설명해.
- 각 여행지의 기후, 주요 관광지를 알려줘.""",

    """가장 추천하는 여행지 한 곳을 선정하고, 거기서 할 수 있는 활동을 제안해.
- 왜 최종 여행지로 선정했는지 설명해.
- 해당 여행지에서 즐길 수 있는 다섯 가지 활동을 나열해.
- 자연 탐방, 역사 탐방, 음식 체험 등 다양한 영역의 활동을 골라줘.""",

    """추천한 여행지의 하루 일정 계획을 세워줘.
- 오전, 오후, 저녁으로 나눠 일정을 짜줘.
- 각 시간대에 어떤 활동을 하면 좋을지 설명해.""",
]

# ============================================
# 프롬프트 체이닝 함수 (개선 버전)
# ============================================
def prompt_chain_workflow(initial_input: str, prompt_chain: List[str]) -> List[str]:
    response_chain = []
    final_prompts = []
    previous_response = initial_input

    for i, prompt in enumerate(prompt_chain, 1):
        final_prompt = f"""{prompt}

처음에 사용자가 입력한 내용은 다음과 같아. 응답할 때 항상 이 내용을 고려해.
{initial_input}

또한 응답 시 아래 내용도 참고해.
{previous_response}"""

        final_prompts.append(final_prompt)
        response = fake_llm_call(final_prompt)   # ← 가짜 LLM 호출
        response_chain.append(response)
        previous_response = response

    return response_chain, final_prompts

# ============================================
# 메인: Streamlit UI
# ============================================
def main():
    st.set_page_config(page_title="프롬프트 체이닝 에이전트", layout="wide")
    st.title("프롬프트 체이닝 에이전트 (여행 일정 수립)")

    # 사용자 입력 영역
    initial_input = st.text_area(
        "여행 스타일 입력",
        value="""따뜻한 날씨를 좋아하고 자연 경관과 역사적인 장소를 둘러보는 걸 선호해."""
    )

    # 단계별 프롬프트 편집 영역
    custom_prompts = []
    with st.expander("⚙ 단계별 프롬프트 설정", expanded=False):
        for i, default_prompt in enumerate(default_prompts, 1):
            edited = st.text_area(
                f"프롬프트 {i}",
                value=default_prompt,
                height=140,
                key=f"prompt_{i}"
            )
            custom_prompts.append(edited)

    # 실행 버튼
    if st.button("🚀 프롬프트 체인 실행"):
        final_result_tab, details_tab = st.tabs(["✨ 최종 결과", "🔄 세부 단계"])

        with st.spinner("실행 중입니다..."):
            results, final_prompts = prompt_chain_workflow(initial_input, custom_prompts)

        with final_result_tab:
            st.write(results[-1])

        with details_tab:
            for i in range(len(custom_prompts)):
                with st.expander(f"📝 {i+1} 단계: 프롬프트와 응답", expanded=False):
                    st.markdown("===== 프롬프트 =====")
                    st.code(final_prompts[i])
                    st.markdown("===== 응답 =====")
                    st.write(results[i])

if __name__ == "__main__":
    main()
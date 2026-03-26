import streamlit as st
import ollama

# ============================================
# 1. 라우터 & LLM 호출 함수
# ============================================
def select_model_for_task(task_type: str, text: str = "") -> str:
    """
    작업 유형(task_type) 및 내용에 따라 최적의 모델을 선택합니다.
    """
    if task_type == "analysis":
        # 복잡한 분석(Gap Analysis, Action Plan)은 추론 능력이 뛰어난 모델 사용
        return "qwen3:8b"
    
    # 일반 대화(multi-turn 코칭)는 qwen2.5:7b를 기본으로 하되, 
    # 코딩/수학 등 기술적 내용이 포함되면 8b로 라우팅
    text_lower = text.lower()
    complex_keywords = ["코드", "코딩", "파이썬", "알고리즘", "수학", "논리", "분석"]
    
    if any(kw in text_lower for kw in complex_keywords):
        return "qwen3:8b"
    return "qwen2.5:7b"

def llm_chat_call(messages: list, model: str) -> str:
    """Ollama API를 통해 멀티턴 대화 히스토리를 전달하고 응답을 받습니다."""
    try:
        response = ollama.chat(model=model, messages=messages)
        return response["message"]["content"].strip()
    except Exception as e:
        return f"통신 에러가 발생했습니다: {str(e)}"

# ============================================
# 2. 메인 UI 및 에이전트 로직
# ============================================
def main():
    st.set_page_config(page_title="AI 코칭 에이전트", layout="centered")
    st.title("🎯 AI 코칭 에이전트")
    st.caption("당신의 목표 달성을 돕는 1:1 러닝 코치입니다.")

    # --- 세션 상태 초기화 ---
    if "goal" not in st.session_state:
        st.session_state.goal = ""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "session_ended" not in st.session_state:
        st.session_state.session_ended = False

    # --- Step 1: 단기 목표 입력창 ---
    if not st.session_state.goal:
        st.info("👋 환영합니다! 코칭을 시작하기 위해 달성하고자 하는 단기 목표를 알려주세요.")
        goal_input = st.text_input("단기 목표 (예: 한 달 안에 파이썬 크롤링 마스터하기, 토익 800점 달성 등)")
        
        if st.button("코칭 시작하기", type="primary"):
            if goal_input.strip():
                st.session_state.goal = goal_input
                
                # 코치의 첫 질문 생성 (현재 수준 파악)
                system_prompt = {
                    "role": "system",
                    "content": f"당신은 전문적이고 공감 능력이 뛰어난 학습 코치입니다. 학생의 단기 목표는 '{goal_input}'입니다. 첫 인사와 함께, 이 목표를 달성하기 위해 학생의 현재 수준이나 경험, 상황을 파악할 수 있는 질문을 딱 1~2개만 던져주세요."
                }
                st.session_state.messages.append(system_prompt)
                
                with st.spinner("코치가 상황을 분석하고 질문을 준비 중입니다..."):
                    model = select_model_for_task("chat", goal_input)
                    first_reply = llm_chat_call(st.session_state.messages, model)
                    
                    st.session_state.messages.append({"role": "assistant", "content": first_reply})
                st.rerun()
            else:
                st.warning("목표를 입력해주세요!")
        return # 목표 설정 전에는 아래 로직 실행 안 함

    # --- Step 2: 멀티턴 코칭 세션 (진행 중) ---
    st.sidebar.subheader("📌 나의 현재 목표")
    st.sidebar.info(st.session_state.goal)
    
    # 대화 히스토리 출력 (system 프롬프트 제외)
    for msg in st.session_state.messages:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    # 세션이 아직 진행 중일 때만 채팅 입력창과 종료 버튼 표시
    if not st.session_state.session_ended:
        user_input = st.chat_input("코치에게 답장을 보내세요...")
        
        # 채팅 입력 시
        if user_input:
            # 1. 사용자 메시지 화면에 표시 및 저장
            with st.chat_message("user"):
                st.markdown(user_input)
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 2. 모델 라우팅 및 LLM 호출
            model_to_use = select_model_for_task("chat", user_input)
            with st.chat_message("assistant"):
                with st.spinner(f"코치가 답변을 작성 중입니다... (사용 모델: {model_to_use})"):
                    # 코칭 프롬프트 강화를 위해 시스템 메시지를 교체/유지하는 것도 가능하지만,
                    # 여기서는 전체 히스토리를 그대로 넘겨 문맥을 유지합니다.
                    coach_reply = llm_chat_call(st.session_state.messages, model_to_use)
                    st.markdown(coach_reply)
            
            st.session_state.messages.append({"role": "assistant", "content": coach_reply})
            st.rerun()

        # 세션 종료 버튼 (사이드바 또는 하단)
        st.sidebar.markdown("---")
        if st.sidebar.button("🛑 세션 종료 및 결과 분석", type="primary", use_container_width=True):
            st.session_state.session_ended = True
            st.rerun()

    # --- Step 3: 세션 종료 및 Gap Analysis / Action Plan 도출 ---
    if st.session_state.session_ended:
        st.divider()
        st.subheader("📊 코칭 세션 결과 보고서")
        
        # 분석을 위한 프롬프트 구성 (히스토리 기반)
        analysis_prompt = """
        지금까지의 대화를 바탕으로, 코치로서 학생을 위한 최종 리포트를 작성해주세요.
        반드시 다음 두 가지 섹션을 포함해야 합니다:
        
        1. **Gap Analysis (격차 분석)**: 학생의 목표와 현재 수준 사이의 차이점, 부족한 점 분석
        2. **Action Plan (실행 계획)**: 목표 달성을 위한 구체적이고 실현 가능한 단계별(Step-by-step) 행동 지침
        
        마크다운을 활용해 가독성 좋고 명확하게 작성해주세요.
        """
        
        # 분석용 임시 메시지 리스트 생성
        analysis_messages = st.session_state.messages.copy()
        analysis_messages.append({"role": "user", "content": analysis_prompt})
        
        # 분석은 항상 가장 똑똑한 모델(qwen3:8b)을 사용하도록 강제
        analysis_model = select_model_for_task("analysis")
        
        with st.spinner(f"대화 내용을 분석하여 Action Plan을 생성 중입니다... ({analysis_model})"):
            final_report = llm_chat_call(analysis_messages, analysis_model)
        
        st.success("✅ 분석이 완료되었습니다!")
        with st.container(border=True):
            st.markdown(final_report)
            
        if st.button("🔄 새로운 목표로 다시 시작하기"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    main()
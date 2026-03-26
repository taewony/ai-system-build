import streamlit as st
import ollama
from typing import List, Tuple

# ============================================
# 1. 라우터: 프롬프트 내용에 따른 모델 자동 선택
# ============================================
def classify_task_and_select_model(text: str) -> str:
    """
    텍스트를 분석하여 qwen3:8b 또는 qwen2.5:7b를 선택합니다.
    """
    text_lower = text.lower()
    
    # qwen3:8b 사용 조건 (기술적, 복잡한 추론)
    complex_keywords = [
        "코드", "코딩", "python", "sql", "수학", "미분", "적분", 
        "논리", "추론", "알고리즘", "데이터", "분석", "architecture"
    ]
    
    if any(kw in text_lower for kw in complex_keywords):
        return "qwen3:8b"
    else:
        return "qwen2.5:7b"

def llm_call(prompt: str, model: str) -> str:
    """Ollama API 호출"""
    try:
        response = ollama.chat(model=model, messages=[{"role": "user", "content": prompt}])
        return response["message"]["content"].strip()
    except Exception as e:
        return f"에러 발생: {str(e)}"

# ============================================
# 2. 메인 UI 및 로직
# ============================================
def main():
    st.set_page_config(page_title="Dynamic Prompt Chaining", layout="wide")
    st.title("🔗 동적 프롬프트 체이닝 & 스마트 라우터")
    st.markdown("단계별로 프롬프트를 추가하고, 내용에 따라 **Qwen3(8B)** 또는 **Qwen2.5(7B)**가 자동으로 할당됩니다.")

    # 세션 상태 초기화 (프롬프트 단계 관리)
    if "steps" not in st.session_state:
        st.session_state.steps = [
            "사용자의 취향을 요약하고 적합한 여행지 3곳을 추천해줘.",
            "선택된 여행지들 중 가성비 분석해서 좋은 곳 하나를 골라줘.",
            "해당 장소의 1일 여행 코스를 표 형식으로 작성해줘."
        ]

    # --- UI: 입력 영역 ---
    col1, col2 = columns = st.columns([1, 1.2], gap="large")

    with col1:
        st.subheader("🛠 체인 구성")
        initial_input = st.text_input("🎯 시작 아이디어/데이터", value="일본 교토 여행, 조용한 사찰 위주")
        
        # 동적 프롬프트 입력창 생성
        updated_steps = []
        for i, step_content in enumerate(st.session_state.steps):
            with st.expander(f"Step {i+1} 프롬프트", expanded=True):
                # 개별 모델 미리보기 (라우팅 로직 시각화)
                suggested_model = classify_task_and_select_model(step_content)
                st.caption(f"예상 모델: `{suggested_model}`")
                
                text = st.text_area(f"내용 작성", value=step_content, key=f"step_input_{i}", height=100)
                updated_steps.append(text)
        
        st.session_state.steps = updated_steps

        # 버튼 레이아웃
        btn_col1, btn_col2 = st.columns(2)
        if btn_col1.button("➕ 단계 추가"):
            st.session_state.steps.append("")
            st.rerun()
        
        if btn_col2.button("🗑 마지막 단계 삭제") and len(st.session_state.steps) > 1:
            st.session_state.steps.pop()
            st.rerun()

        run_button = st.button("🚀 체인 실행 시작", use_container_width=True, type="primary")

    # --- UI: 결과 출력 영역 ---
    with col2:
        st.subheader("📊 실행 결과")
        if run_button:
            previous_response = initial_input
            
            for i, prompt_template in enumerate(st.session_state.steps):
                if not prompt_template.strip():
                    continue
                
                # 1. 모델 선택 (현재 단계 프롬프트 기준)
                model_to_use = classify_task_and_select_model(prompt_template)
                
                with st.status(f"단계 {i+1} 처리 중... ({model_to_use})", expanded=True) as status:
                    # 2. 프롬프트 구성 (컨텍스트 병합)
                    full_prompt = f"""[이전 맥락]: {previous_response}\n\n[지시 사항]: {prompt_template}"""
                    
                    # 3. LLM 호출
                    response = llm_call(full_prompt, model_to_use)
                    
                    # 4. 결과 출력
                    st.markdown(f"**Step {i+1} 결과** ({model_to_use})")
                    st.write(response)
                    
                    previous_response = response # 다음 단계를 위해 저장
                    status.update(label=f"단계 {i+1} 완료!", state="complete", expanded=False)
            
            st.success("✅ 모든 체인이 완료되었습니다.")
            with st.expander("📝 최종 결과물 복사하기"):
                st.code(previous_response)

if __name__ == "__main__":
    main()
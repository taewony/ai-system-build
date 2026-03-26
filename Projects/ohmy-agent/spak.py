import streamlit as st
from core.agent_loop import run_agent

st.set_page_config(page_title="SPAK 로컬 에이전트", layout="centered")
st.title("🤖 SPAK Agent Kernel (Fake LLM)")

# 대화 기록 상태 관리
if "messages" not in st.session_state:
    st.session_state.messages = []

# 기존 대화 출력
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# 사용자 입력창
if prompt := st.chat_input("에이전트에게 지시를 내려보세요 (예: '지식을 저장해줘')"):
    # 1. 사용자 메시지 화면에 출력 및 저장
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 2. 에이전트 응답 영역
    with st.chat_message("assistant"):
        # 진행 상황이 실시간으로 쓰여질 빈 공간 마련
        status_box = st.empty()
        log_text = ""
        
        # 에이전트 루프 실행 (yield로 하나씩 받아옴)
        for step_data in run_agent(prompt, st.session_state.messages[:-1]):
            msg_type = step_data["type"]
            msg_content = step_data["content"]
            
            if msg_type == "info":
                log_text += f"*{msg_content}*\n\n"
            elif msg_type == "thought":
                log_text += f"🧠 **생각:** {msg_content}\n\n"
            elif msg_type == "action":
                log_text += f"🛠️ **실행:** {msg_content}\n\n"
            elif msg_type == "observation":
                log_text += f"👀 **결과:** {msg_content}\n\n---\n\n"
            elif msg_type == "finish":
                log_text += f"✅ **최종 답변:** {msg_content}"
                # 루프가 끝나면 최종 대화만 세션에 저장 (UI 깔끔하게 유지)
                st.session_state.messages.append({"role": "assistant", "content": msg_content})
                
            # 빈 공간에 누적된 텍스트를 실시간 업데이트
            status_box.markdown(log_text)
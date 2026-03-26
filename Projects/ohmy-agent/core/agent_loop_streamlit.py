import json
import os
from tools.fake_llm import FakeClient

# 파일이 저장될 로컬 작업 공간 (루트 디렉토리 기준)
WORKSPACE_DIR = "./workspace"
os.makedirs(WORKSPACE_DIR, exist_ok=True)

# Fake LLM 클라이언트 초기화 (나중에 진짜 OpenAI 객체로 한 줄만 바꾸면 됩니다)
client = FakeClient()

def execute_tool(action: dict) -> str:
    """LLM이 요청한 도구(Tool)를 실제로 실행하는 함수"""
    tool_name = action.get("tool")
    args = action.get("args", {})
    
    if tool_name == "write_knowledge":
        filepath = os.path.join(WORKSPACE_DIR, args.get("filename"))
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(args.get("content"))
        return f"성공: [{filepath}]에 지식을 저장했습니다."
        
    elif tool_name == "read_knowledge":
        filepath = os.path.join(WORKSPACE_DIR, args.get("filename"))
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            return f"검색 결과: {content}"
        return f"실패: [{filepath}] 파일을 찾을 수 없습니다."
        
    return f"Error: 알 수 없는 도구 '{tool_name}'"

def run_agent(user_input: str, chat_history: list):
    """
    에이전트 무한 루프. Streamlit UI 업데이트를 위해 dict 형태의 상태를 계속 yield 합니다.
    """
    messages = chat_history.copy()
    messages.append({"role": "user", "content": user_input})
    
    yield {"type": "info", "content": "🚀 에이전트 사고 루프 시작..."}
    
    step = 0
    while step < 10: # 무한 루프 방지용 안전 장치 (최대 10턴)
        step += 1
        
        # 1. LLM API 호출 (여기서는 Fake LLM)
        response = client.chat.completions.create(model="fake-model", messages=messages)
        llm_reply = response.choices[0].message.content
        
        # 2. JSON 파싱
        try:
            action = json.loads(llm_reply)
        except Exception as e:
            yield {"type": "error", "content": f"JSON 파싱 실패: {e}"}
            break
            
        # UI로 에이전트의 '생각' 전달
        yield {"type": "thought", "content": action.get("thought", "...")}
        
        # 3. 종료 조건 확인
        if action.get("tool") == "finish":
            yield {"type": "finish", "content": action.get("args", {}).get("message", "")}
            break
            
        # UI로 에이전트의 '행동' 전달
        yield {"type": "action", "content": f"도구: `{action.get('tool')}` | 인수: {action.get('args')}"}
        
        # 4. 실제 도구 실행 및 결과(Observation) 수집
        observation = execute_tool(action)
        
        # UI로 '결과' 전달
        yield {"type": "observation", "content": observation}
        
        # 대화 히스토리에 방금 한 행동과 결과를 추가하여 다시 LLM에게 넘길 준비
        messages.append({"role": "assistant", "content": llm_reply})
        messages.append({"role": "user", "content": f"도구 실행 결과:\n{observation}\n다음 행동을 지시하세요."})
import json
import time
from core.semantic_store import SemanticStore

# SemanticStore 인스턴스 초기화 (작업 폴더는 기본값인 ./workspace 사용)
store = SemanticStore()

def execute_tool(action: dict) -> str:
    """LLM이 요청한 도구(Tool)를 SemanticStore API와 매핑하여 실제 실행합니다."""
    tool_name = action.get("tool")
    args = action.get("args", {})
    
    try:
        if tool_name == "set_book_title":
            return store.set_book_title(args.get("title"))
            
        elif tool_name == "add_chapter":
            return store.add_chapter(args.get("title"), args.get("content_md"))
            
        elif tool_name == "memorize_rule":
            return store.memorize_rule(args.get("given"), args.get("when"), args.get("then"))
            
        elif tool_name == "recall_knowledge":
            return store.recall_knowledge(args.get("query"))
        
        # 1. 쉘 명령어 자율 실행 도구
        elif tool_name == "run_powershell":
            command = args.get("command")
            # subprocess.run을 사용하여 명령어 실행 후 결과 반환
            import subprocess
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, cwd="./")
            return result.stdout if result.returncode == 0 else result.stderr

        # 2. 임의의 파일 작성 도구 (Lit JS 파일 등을 생성하기 위함)
        elif tool_name == "write_file":
            filepath = args.get("path")
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(args.get("content"))
            return f"성공: {filepath} 파일이 작성되었습니다."
        
        else:
            return f"Error: 알 수 없는 도구 '{tool_name}'"
            
    except Exception as e:
        return f"Tool Execution Error: {str(e)}"

def get_simulated_llm_plan() -> list:
    """
    실제 LLM이 "AI Agent Programming 플레이북을 만들어줘"라는 지시를 받고
    Plan-and-Solve 전략에 따라 생성해 낸 일련의 JSON 액션(계획) 리스트입니다.
    """
    return [
        {
            "thought": "[Plan 1/6] 먼저 Playbook의 전체 제목을 설정하고 뼈대를 잡아야겠다.",
            "tool": "set_book_title",
            "args": {"title": "AI Agent Programming"}
        },
        {
            "thought": "[Plan 2/6] 첫 번째 챕터로 Ollama에 대한 내용을 작성하여 파일로 저장하자.",
            "tool": "add_chapter",
            "args": {
                "title": "1. Ollama: Lightweight Local Serving",
                "content_md": "# 1. Ollama\n\nOllama는 GGUF 포맷을 사용하여 로컬 환경에서 가볍게 LLM을 서빙할 수 있는 훌륭한 도구입니다.\n\n"
            }
        },
        {
            "thought": "[Plan 3/6] 두 번째 챕터인 nano-vLLM의 핵심은 GPU 최적화이므로 이 내용을 강조해서 쓰자.",
            "tool": "add_chapter",
            "args": {
                "title": "2. nano-vLLM: GPU Inference",
                "content_md": "# 2. nano-vLLM\n\nnano-vLLM은 Safetensors 포맷의 원본 모델을 GPU VRAM에 통째로 올려 압도적인 추론 속도를 보여줍니다."
            }
        },
        {
            "thought": "[Plan 4/6] 세 번째 챕터, openclaw를 통한 도구 호출(Tool Calling) 마크다운을 작성하자.",
            "tool": "add_chapter",
            "args": {
                "title": "3. OpenClaw: Tool Calling",
                "content_md": "# 3. OpenClaw\n\nOpenClaw는 복잡한 함수 호출과 JSON 파싱을 안정적으로 수행하도록 돕는 프레임워크입니다."
            }
        },
        {
            "thought": "[Plan 5/6] 마지막 챕터로 자율형 에이전트인 Hermes Agent를 다루자.",
            "tool": "add_chapter",
            "args": {
                "title": "4. Hermes Agent: ReAct Loops",
                "content_md": "# 4. Hermes Agent\n\n사용자의 OS 자원을 직접 제어하며 Thought-Action 루프를 도는 강력한 에이전트입니다."
            }
        },
        {
            "thought": "[Plan 6/6] 모든 챕터 작성이 완료되었으므로 작업을 종료하자.",
            "tool": "finish",
            "args": {"message": "성공적으로 'AI Agent Programming' 플레이북의 기초 파일 생성을 완료했습니다! workspace 폴더를 확인해 보세요."}
        }
    ]

def run_agent(user_input: str, chat_history: list):
    """
    Streamlit UI로 진행 상황을 실시간 스트리밍(yield)하는 에이전트 제어 루프
    """
    yield {"type": "info", "content": f"🚀 작업 지시 수신: '{user_input}'\n에이전트가 Plan-and-Solve 전략에 따라 작업을 분해하고 실행을 시작합니다..."}
    
    # 시뮬레이션된 LLM의 계획표(Plan)를 가져옵니다.
    plan_queue = get_simulated_llm_plan()
    
    for step, action in enumerate(plan_queue, 1):
        time.sleep(1.5) # UI 스트리밍 효과를 위해 약간의 지연 추가
        
        # 1. 에이전트의 생각(Thought) 출력
        yield {"type": "thought", "content": action.get("thought")}
        
        # 2. 종료 조건 확인
        if action.get("tool") == "finish":
            yield {"type": "finish", "content": action.get("args", {}).get("message", "")}
            break
            
        # 3. 도구(Action) 호출 정보 출력
        yield {"type": "action", "content": f"도구: `{action.get('tool')}` | 챕터명: {action.get('args', {}).get('title', 'N/A')}"}
        
        # 4. ⭐️ 실제 도구 실행 (SemanticStore를 통해 로컬 파일 조작) ⭐️
        observation = execute_tool(action)
        
        # 5. 실행 결과(Observation) 출력
        yield {"type": "observation", "content": observation}

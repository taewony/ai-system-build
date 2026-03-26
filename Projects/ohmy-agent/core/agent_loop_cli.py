import json
import subprocess
import os
from openai import OpenAI

# ---------------------------------------------------------
# 1. 환경 설정 및 클라이언트 초기화
# ---------------------------------------------------------
# WSL2에서 동작 중인 vLLM 서버의 IP와 포트를 입력합니다.
WSL2_API_BASE = "http://127.0.0.1:8000/v1" 
API_KEY = "EMPTY" # vLLM은 기본적으로 API 키를 무시합니다.
MODEL_NAME = "Qwen/Qwen3-8B"

# 에이전트가 작업할 로컬 PC의 기준 폴더 (보안을 위한 Sandboxing 경계)
WORKSPACE_DIR = r"C:\Users\jovyan\Desktop\TargetProject"

client = OpenAI(base_url=WSL2_API_BASE, api_key=API_KEY)

# ---------------------------------------------------------
# 2. 도구(Tool) 실행 함수 (Windows PowerShell & Python 전용)
# ---------------------------------------------------------
def execute_tool(action: dict) -> str:
    """LLM이 요청한 JSON Action을 파싱하여 실제 OS 명령어를 실행합니다."""
    tool_name = action.get("tool")
    args = action.get("args", {})
    
    try:
        # 1. PowerShell 명령어 실행 도구
        if tool_name == "run_powershell":
            command = args.get("command")
            print(f"\n[🛠️ 실행 중] PowerShell: {command}")
            # cwd 지정으로 workspace 밖으로 나가는 것을 일차적으로 방어
            result = subprocess.run(
                ["powershell", "-Command", command],
                cwd=WORKSPACE_DIR,
                capture_output=True,
                text=True,
                timeout=30 # 무한 대기 방지
            )
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"

        # 2. Workspace 내의 파이썬 스크립트 실행 도구
        elif tool_name == "run_python_script":
            script_name = args.get("script_name")
            script_path = os.path.join(WORKSPACE_DIR, script_name)
            
            # 경로 이탈 검증 (Path Traversal 방어)
            if not os.path.abspath(script_path).startswith(os.path.abspath(WORKSPACE_DIR)):
                return "Error: Permission denied. Cannot access files outside workspace."
                
            print(f"\n[🛠️ 실행 중] Python Script: {script_name}")
            result = subprocess.run(
                ["python", script_path],
                cwd=WORKSPACE_DIR,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout if result.returncode == 0 else f"Error: {result.stderr}"
            
        else:
            return f"Error: Unknown tool '{tool_name}'"
            
    except Exception as e:
        return f"Error during execution: {str(e)}"

# ---------------------------------------------------------
# 3. 에이전트 핵심 무한 루프 (The ReAct Loop)
# ---------------------------------------------------------
def agent_loop(user_goal: str):
    print(f"🚀 [Agent 시작] 목표: {user_goal}")
    print(f"📁 [Workspace] {WORKSPACE_DIR}\n")
    
    # 시스템 프롬프트: 에이전트의 역할과 JSON 출력 규칙을 엄격하게 강제합니다.
    system_prompt = """
    당신은 Windows PC에서 동작하는 자율형 개발 에이전트입니다.
    당신은 다음 두 가지 도구만 사용할 수 있습니다:
    1. {"tool": "run_powershell", "args": {"command": "dir"}}
    2. {"tool": "run_python_script", "args": {"script_name": "main.py"}}
    
    목표를 달성하기 위해 행동이 필요하다면 반드시 위 형식의 순수 JSON만 출력하세요.
    목표를 완전히 달성했다면, {"tool": "finish", "args": {"message": "최종 결과 설명"}} 형식으로 출력하세요.
    """
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_goal}
    ]
    
    step = 1
    while True:
        print(f"\n--- [Step {step}] LLM 추론 중... ---")
        
        # 1. Thought (LLM 호출)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1 # 명확한 로직 실행을 위해 낮은 온도 유지
        )
        
        llm_reply = response.choices[0].message.content.strip()
        print(f"🧠 [Agent의 판단]\n{llm_reply}")
        
        # 메시지 히스토리에 판단 기록
        messages.append({"role": "assistant", "content": llm_reply})
        
        # 2. Parse (JSON 파싱 시도)
        try:
            # LLM이 마크다운 코드 블록(```json)을 씌웠을 경우를 대비한 텍스트 정제
            clean_json_str = llm_reply.replace("```json", "").replace("```", "").strip()
            action = json.loads(clean_json_str)
        except json.JSONDecodeError:
            # 포맷 오류 시 스스로 수정하도록 피드백 (Self-Correction)
            error_msg = "Error: 응답이 올바른 JSON 형식이 아닙니다. 순수 JSON 형식으로 다시 시도하세요."
            print(f"⚠️ {error_msg}")
            messages.append({"role": "user", "content": error_msg})
            step += 1
            continue

        # 3. Action & Observation (종료 조건 확인 및 도구 실행)
        if action.get("tool") == "finish":
            print(f"\n✅ [목표 달성 완료]\n{action.get('args', {}).get('message')}")
            break
            
        # 도구 실행 후 결과를 관찰(Observation)하여 히스토리에 추가
        observation = execute_tool(action)
        print(f"👀 [실행 결과 (Observation)]\n{observation}")
        
        messages.append({
            "role": "user", 
            "content": f"명령어 실행 결과:\n{observation}\n\n이 결과를 바탕으로 다음 행동을 JSON으로 지시하세요."
        })
        
        step += 1

# ---------------------------------------------------------
# 4. 실행 진입점
# ---------------------------------------------------------
if __name__ == "__main__":
    # 테스트 목표 하드코딩 (실제 구현 시 argparse 등을 통해 입력받음)
    goal = "현재 Workspace 폴더에 있는 파일 목록을 확인하고, 'hello.py'라는 파일이 없다면 'print(\"Hello Agent\")' 코드를 담은 hello.py를 생성한 뒤 실행해줘."
    agent_loop(goal)
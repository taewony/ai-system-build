# SPAK-WinCLI: Spec-Driven Autonomous Agent for Windows

SPAK-WinCLI는 Windows PowerShell 환경에서 동작하는 로컬 자율형 AI 에이전트 커널입니다. 
에이전트는 지정된 로컬 PC의 작업 폴더(Workspace) 내에서 자율적으로 파일을 읽고, 문서를 수정하며, PowerShell 명령어를 실행하여 주어진 목표를 달성합니다. 무거운 LLM 추론은 GPU 자원을 가진 서버나 WSL2 환경에서의 전용 로컬 게이트웨이로 오프로딩하여 로컬 데스크톱 자원 점유를 최소화합니다.

## 🏗 Architecture

이 프로젝트는 **Agent Kernel(Windows)**과 **LLM Gateway(WSL2)**가 분리된 구조를 가집니다.

* **Frontend / Agent Kernel (Windows 11/10):**
  * PowerShell CLI 기반으로 동작하는 Python 에이전트 루프.
  * AgentSpec 기반의 선언적 목표 설정 및 프롬프트 관리.
  * 로컬 파일 시스템 접근 및 Windows 네이티브 도구(Tools) 실행 (`subprocess` 활용).
* **Backend / LLM Gateway (WSL2):**
  * vLLM (또는 Ollama) 기반의 초고속 LLM 서빙 엔진.
  * OpenAI API 규격 완벽 호환 (`http://localhost:8000/v1`).
  * L40S 등 로컬 GPU 자원을 독점하여 추론 속도 극대화.

## ✨ Key Features

* **Local Workspace Control:** 샌드박스화된 로컬 작업 폴더 내에서 파일 생성, 파싱, 수정 등 OS 밀착형 작업 수행.
* **Spec-Driven Execution:** YAML/JSON 형태의 `AgentSpec`을 통해 에이전트의 페르소나, 사용 가능한 도구(Tools), 제약 사항을 동적으로 주입.
* **Autonomous ReAct Loop:** Thought -> Action -> Observation 패턴을 통한 자율적 문제 해결 및 자기 검증(Self-Correction).
* **PowerShell Native:** Windows 시스템 제어, 레지스트리 읽기, 로컬 앱 실행 등 PowerShell의 강력한 기능을 Agent의 Tool로 활용.

## 🚀 Getting Started

### Prerequisites

1. **WSL2 Backend:** WSL2 환경에 OpenAI API 호환 LLM 서버가 실행 중이어야 합니다.
   ```bash
   # WSL2 터미널 예시 (vLLM 구동)
   python -m vllm.entrypoints.openai.api_server --model Qwen/Qwen3-8B
   ```
2. **Windows Frontend:** Python 3.10 이상 권장.

### Installation

Windows PowerShell을 열고 아래 명령어를 순서대로 실행합니다.

```powershell
# 1. Clone the repository
git clone [https://github.com/your-org/SPAK-WinCLI.git](https://github.com/your-org/SPAK-WinCLI.git)
cd SPAK-WinCLI

# 2. Create a virtual environment & install dependencies
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt

# 3. Setup Environment Variables
cp .env.example .env
# .env 파일을 열어 WSL2 API 주소를 확인합니다. (기본값: http://localhost:8000/v1)
```

### Usage

작업을 수행할 로컬 폴더 경로와 실행할 Spec을 지정하여 에이전트를 구동합니다.

```powershell
python core/agent_loop.py --spec specs/code_review_spec.yaml --workspace C:\Users\jovyan\Desktop\TargetProject
```

## 📂 Directory Structure

```text
SPAK-WinCLI/
├── core/                   # 에이전트 커널 및 실행 루프 로직
│   ├── agent_loop.py       # 메인 ReAct 무한 루프
│   ├── spec_parser.py      # AgentSpec 파싱 및 프롬프트 빌더
│   └── memory.py           # 단기/장기 메모리 관리 (상태 유지)
├── tools/                  # 에이전트가 호출할 수 있는 로컬 도구 모음
│   ├── file_system.py      # 파일 읽기/쓰기/탐색
│   └── shell_executor.py   # PowerShell 명령어 안전 실행
├── specs/                  # 에이전트 역할 및 목표 명세서 (AgentSpec DSL)
│   ├── default_spec.yaml
│   └── code_review_spec.yaml
├── workspace/              # 에이전트가 기본적으로 활동할 격리된 로컬 폴더
├── requirements.txt
└── README.md
```

## 🛡️ Security & Sandboxing

* **주의:** 에이전트에게 시스템(PowerShell) 제어 권한을 부여하므로, 초기 테스트 시에는 파괴적인 명령어(`rm`, `del` 등) 실행을 제한하는 **Dry-run 모드**나 사용자 승인(Human-in-the-loop) 프롬프트를 활성화하는 것을 권장합니다.
* 모든 파일 작업은 지정된 `workspace` 디렉토리 내부로 제한되도록 `tools/file_system.py`에 경로 검증(Path Traversal 방지)이 구현되어야 합니다.

# 📄 [SPAK-Publishing] AI 에이전트 기반 Playbook 자동화 시스템 설계서

## 1. 시스템 개요 (System Overview)
본 시스템은 출판사 및 교육 콘텐츠 제작자가 마크다운(MD) 형태의 피드백이나 지시사항을 업로드하면, AI 에이전트가 이를 분석해 전체 작업을 하위 태스크로 분해(Plan-and-Solve)하고, 필요한 정보를 검색 및 생성하여 **Lit + Vite 기반의 웹 플레이북(Online Playbook) 소스 코드를 자율적으로 작성하고 갱신하는 시스템**입니다.

---

## 2. 핵심 요구사항 명세 (Requirements Specification)

### 2.1. Agent Core 요구사항
* **작업 분해 (Task Planning):** 사용자의 MD 지시서를 분석하여 의존성이 있는 하위 태스크(Sub-tasks) 리스트로 분해해야 합니다. (예: 1. 정보 검색 -> 2. 목차 YAML 수정 -> 3. Chapter 1 HTML 생성)
* **도구 활용 (Tool Calling):**
    * *File I/O:* 로컬 작업 폴더의 YAML, MD, HTML(Lit) 파일을 읽고 씁니다.
    * *Web Search:* 최신 정보나 기술 문서가 필요할 때 검색 API(예: Tavily, DuckDuckGo)를 호출합니다.
    * *Heavy LLM Offloading:* 대량의 텍스트나 복잡한 HTML/CSS 컴포넌트 생성이 필요할 때는 로컬 LLM 대신 클라우드 LLM(Gemini API/CLI)을 호출하여 작업을 위임합니다.
* **워크스페이스 동기화:** 에이전트가 코드를 수정하면 `vite run dev`로 구동 중인 플레이북에 HMR(Hot Module Replacement)이 즉시 반영되어야 합니다.

### 2.2. SemanticStore 요구사항
* **엔티티-관계(Entity-Relation) 관리:** `BOOK`과 `CHAPTER` 엔티티를 YAML/MD 파일로 저장하고, 이들 간의 계층 구조와 하이퍼링크 매핑 정보를 관리해야 합니다.
* **경험 지식 축적 (BDD 기반):** 에이전트가 과거에 겪은 시행착오나 콘텐츠 작성 가이드라인을 `Given-When-Then` 형식의 룰(Rule)로 저장하고 검색할 수 있어야 합니다.
    * *예:* `Given` (표를 만들 때) `When` (데이터가 5줄 이상이면) `Then` (Lit 데이터그리드 컴포넌트를 사용한다.)
* **점진적 진화 (Evolutionary Architecture):** 초기(Phase 1)에는 Python Dictionary와 `json`/`yaml` 파일 시스템 조합으로 In-memory 환경에서 가볍게 동작하며, 추후(Phase 3) LlamaIndex + GraphDB(Neo4j) 구조로 전환할 수 있도록 인터페이스(Facade)가 분리되어야 합니다.

### 2.3. Streamlit 제어판 (SPAK Dashboard) 요구사항
* **Playbook 프리뷰 (미리보기):** 생성 중인 플레이북 화면(Vite 서버 결과물)을 iframe 형태로 표시하거나, 바로가기 링크를 제공해야 합니다.
* **작업 지시 인터페이스:** 사용자가 검토 후 작성한 수정 요청사항(`.md`)을 업로드할 수 있는 File Uploader 컴포넌트가 필요합니다.
* **실시간 모니터링:** 에이전트의 현재 상태(상위 계획, 진행 중인 Sub-task, Gemini 호출 여부, 완료 퍼센티지)를 실시간 로그 스트리밍과 Progress Bar로 시각화해야 합니다.

---

## 3. 상위 아키텍처 설계 (High-Level Design)

시스템은 크게 4개의 독립된 컨텍스트로 구성됩니다.

1.  **SPAK Dashboard (Streamlit):** 인간(사용자)과 에이전트 간의 소통 창구.
2.  **Agent Kernel (Python/vLLM):** 판단, 계획, 도구 실행을 관장하는 두뇌.
3.  **Semantic Store (Python Facade):** 메타데이터 및 지식 베이스 관리.
4.  **Target Playbook (Vite/Lit):** 에이전트가 조작하는 최종 결과물 환경.

### ⚙️ 시스템 동작 흐름 (Workflow)
1.  **[User]** Streamlit 대시보드에 접속하여 `revision_request.md` 업로드.
2.  **[Dashboard]** 에이전트 커널에 작업 트리거.
3.  **[Agent Kernel]** SemanticStore에서 현재 `BOOK`의 목차(YAML)와 작성 가이드라인(Given-When-Then)을 조회.
4.  **[Agent Kernel]** 수정안을 바탕으로 5단계 Sub-task 플랜 생성.
5.  **[Agent Kernel]** 루프를 돌며 각 태스크 실행.
    * *경량 수정:* 로컬 vLLM이 직접 파일 조작.
    * *대규모 HTML 생성:* Gemini API/CLI Tool 호출 -> 결과물 수신.
6.  **[Agent Kernel]** 수정된 내용을 `workspace/` 내의 파일로 저장.
7.  **[Playbook Server]** 파일 변경을 감지하고 Vite HMR을 통해 즉시 브라우저 화면 갱신.
8.  **[Dashboard]** 모든 태스크 완료 시 사용자에게 "작업 완료" 알림 및 로그 제공.

---

## 4. 단계별 구현 마일스톤 (Phased Implementation Plan)

처음부터 완벽한 시스템을 짜려다 보면 지치기 쉽습니다. 제안해주신 'Python 딕셔너리로 실험'한다는 아이디어를 반영하여 아래의 4단계로 진화시키는 것을 권장합니다.

### Phase 1: MVP (최소 기능 제품) 구축
* **목표:** Streamlit UI와 에이전트 간의 연결 고리 확보, 파일 기반의 단순 Store 구현.
* **구현:**
    * Streamlit 파일 업로더 구현.
    * `SemanticStore` 클래스를 만들어 Python `dict`와 `json` 패키지만을 이용해 BOOK-CHAPTER 관계를 읽고 쓰는 기능 개발.
    * 에이전트가 로컬에 빈 파일(`.html`, `.yaml`)을 생성하는 테스트 루프 작성.

### Phase 2: Plan-and-Solve 아키텍처 & Gemini 연동
* **목표:** 에이전트의 지능 고도화.
* **구현:**
    * 업로드된 지시서를 Sub-task 배열로 쪼개는 프롬프트 엔지니어링 적용.
    * 에이전트 Tool에 `call_gemini(prompt)` 함수를 추가하여, 복잡한 Lit 컴포넌트 마크업을 Gemini가 생성하도록 위임. (CLI보다는 Python SDK 사용을 권장합니다.)

### Phase 3: Web Search & Vite HMR 연동
* **목표:** 외부 정보 수집 및 실시간 결과 확인.
* **구현:**
    * DuckDuckGo 또는 Tavily API를 Tool로 추가.
    * Streamlit 대시보드 화면을 2분할(Columns)하여, 왼쪽에는 에이전트 진행 상황 로그를, 오른쪽에는 `iframe`으로 `localhost:5173` (Vite 서버)를 띄워 실시간 편집 장면을 감상할 수 있게 구성.

### Phase 4: SemanticStore의 LlamaIndex 전환
* **목표:** 본격적인 지식 확장 및 고도화.
* **구현:**
    * 기존의 Python Dict를 걷어내고, 인터페이스는 그대로 둔 채 내부 로직만 LlamaIndex + 로컬 VectorDB(Chroma)로 교체.
    * 에이전트가 작업을 마칠 때마다 "이번 작업에서 배운 점"을 추출해 Given-When-Then 형태로 스스로 Store에 기록(Self-Learning)하는 로직 추가.

---

**전문가의 추가 조언 (Gemini 연동 관련):**
Gemini CLI를 `subprocess`로 호출하는 것도 좋지만, Python 환경이라면 `google-genai` 라이브러리를 설치하여 Agent의 Tool 함수 안에서 직접 API를 찌르는 것이 JSON 응답을 파싱하거나 에러를 제어할 때 훨씬 안정적입니다. 

### 1. PC 동작 및 자원 접근 방식 (Terminal Backend)

`hermes-agent`는 단순한 챗봇 래퍼(Wrapper)가 아니라, **사용자의 OS 환경에 상주하며 자원을 직접 제어하는 '자율형 운영체제 에이전트'**에 가깝습니다.

* **직접적인 자원 접근 (Local Mode):** 에이전트에게 터미널 권한을 부여하면, WSL2 환경 내의 파일 시스템을 읽고 쓰며, 디렉토리를 탐색하고, 파이썬 스크립트를 직접 작성해 실행할 수 있습니다. 
* **샌드박싱 (Sandboxing):** 보안을 위해 PC 자원 접근 수준을 5가지 백엔드(Local, Docker, SSH, Singularity, Modal)로 나누어 격리할 수 있습니다. 예를 들어 Docker 모드로 실행하면, 에이전트가 사고를 치더라도 호스트 PC(WSL2)가 아닌 격리된 컨테이너 내부에서만 명령어가 실행됩니다.
* **플랫폼 확장:** 백그라운드 서비스(Gateway)로 돌려놓고, 텔레그램이나 디스코드 같은 메신저를 통해 외부에서 내 PC(WSL2)에 접속해 있는 에이전트에게 작업을 지시할 수도 있습니다.

### 2. Python으로 구현된 에이전트 루프(Agent Loop)의 핵심 원리

이 에이전트의 심장인 '에이전트 루프'는 Python의 표준적인 **Tool Calling (함수 호출)** 패턴을 고도화한 형태로 구현되어 있습니다.

**A. 무한 사고 루프 (The Execution Loop)**
Python의 `while` 루프를 기반으로 다음의 과정을 반복합니다.
1.  **Thought (생각):** 사용자의 명령(예: "현재 폴더의 로그 파일을 분석해줘")을 LLM에 전달.
2.  **Action (행동 결정):** LLM이 JSON 형태로 어떤 도구(Tool)를 사용할지 응답. (예: `{"tool": "run_shell_command", "args": {"cmd": "cat error.log"}}`)
3.  **Execution (실행):** Python 코드가 이 JSON을 파싱하여 실제 PC 자원을 건드리는 함수를 실행.
4.  **Observation (관찰):** Python 코드가 실행 결과(명령어 출력값)를 수집하여 다시 LLM의 컨텍스트(프롬프트)에 밀어 넣음.
5.  목표를 달성할 때까지 1~4번 반복.

**B. PC 자원 제어 로직 구현 (Tools & Plugins)**
실제로 PC 자원을 건드리는 로직은 놀랍도록 단순한 Python 내장 라이브러리로 이루어져 있습니다.
* **명령어 실행:** Python의 `subprocess.run()` 모듈을 사용하여 쉘 명령어를 실행하고 `stdout`(표준 출력)과 `stderr`(에러)를 캡처하여 LLM에게 돌려줍니다.
* **동시성 처리:** 이번 버전에 추가된 기능으로, 여러 개의 도구를 동시에 써야 할 때 Python의 `ThreadPoolExecutor`를 사용하여 멀티스레딩으로 지연 시간을 대폭 줄입니다.
* **플러그인 아키텍처:** `~/.hermes/plugins/` 디렉토리에 Python 파일을 던져 넣기만 하면, 데코레이터를 통해 에이전트가 즉시 새로운 도구(예: 크롬 브라우저 제어)로 인식하고 사용할 수 있습니다.

---

### Spec-driven Programmable Agent Kernel

`hermes-agent`는 훌륭한 참고 자료지만, 이를 그대로 설치하면 **에이전트가 WSL2라는 리눅스 생태계 안에 갇히게 됩니다.** 만약 선생님께서 엑셀, 윈도우 폴더, 로컬 윈도우 애플리케이션 등 **'Windows 네이티브 자원'**을 주무르는 데스크톱 에이전트를 원하신다면, `hermes-agent`의 Python 루프 설계 사상(프롬프트 구조, Tool Calling 파싱 방식 등)만 벤치마킹하시고, **실제 에이전트 파이썬 코드는 Windows 쪽에 직접 구현하시는 것이 맞습니다.**

`hermes-agent`의 소스 코드 구조 중에서, LLM이 뱉어낸 Tool 호출 JSON을 파싱하여 Python의 `subprocess`로 안전하게 실행하는 **핵심 루프(Loop) 코드의 뼈대**를 추출해서 보여드릴까요? 직접 Windows용 에이전트를 만드실 때 큰 도움이 될 것입니다.

이 구조는 Windows 네이티브 환경의 자원(파일, 프로세스, 앱)을 완벽하게 제어하면서도, 무거운 LLM 연산은 WSL2의 GPU 환경으로 오프로딩하는 매우 실용적이고 강력한 아키텍처입니다.

특히, 에이전트의 동작 방식을 명세화(Spec-driven)하여 구동하는 프로그래머블한 커널(Programmable Agent Kernel) 형태의 프로젝트를 구성하기에 아주 적합합니다.

요청하신 아키텍처를 기반으로 작성한 최상위 README.md 초안입니다. 프로젝트 성격에 맞게 프로젝트명(여기서는 가칭 SPAK-WinCLI로 두었습니다)이나 세부 사항을 수정해서 사용하시면 됩니다.

---

# SPAK-WinCLI: Spec-Driven Autonomous Agent for Windows

SPAK-WinCLI는 Windows PowerShell 환경에서 동작하는 로컬 자율형 AI 에이전트 커널입니다.   
에이전트는 지정된 로컬 PC의 작업 폴더(Workspace) 내에서 자율적으로 파일을 읽고, 문서를 수정하며, PowerShell 명령어를 실행하여 주어진 목표를 달성합니다. 무거운 LLM 추론은 WSL2 환경의 전용 로컬 게이트웨이로 오프로딩하여 데스크톱 자원 점유를 최소화합니다.

## 🏗 Architecture

이 프로젝트는 **Agent Kernel(Windows)**과 **LLM Gateway(WSL2)**가 분리된 구조를 가집니다.

\* **\*\*Frontend / Agent Kernel (Windows 11/10):\*\***  
  \* PowerShell CLI 기반으로 동작하는 Python 에이전트 루프.  
  \* AgentSpec 기반의 선언적 목표 설정 및 프롬프트 관리.  
  \* 로컬 파일 시스템 접근 및 Windows 네이티브 도구(Tools) 실행 (\`subprocess\` 활용).  
\* **\*\*Backend / LLM Gateway (WSL2):\*\***  
  \* vLLM (또는 Ollama) 기반의 초고속 LLM 서빙 엔진.  
  \* OpenAI API 규격 완벽 호환 (\`http://localhost:8000/v1\`).  
  \* L40S 등 로컬 GPU 자원을 독점하여 추론 속도 극대화.

\#\# ✨ Key Features

\* **\*\*Local Workspace Control:\*\*** 샌드박스화된 로컬 작업 폴더 내에서 파일 생성, 파싱, 수정 등 OS 밀착형 작업 수행.  
\* **\*\*Spec-Driven Execution:\*\*** YAML/JSON 형태의 \`AgentSpec\`을 통해 에이전트의 페르소나, 사용 가능한 도구(Tools), 제약 사항을 동적으로 주입.  
\* **\*\*Autonomous ReAct Loop:\*\*** Thought \-\> Action \-\> Observation 패턴을 통한 자율적 문제 해결 및 자기 검증(Self-Correction).  
\* **\*\*PowerShell Native:\*\*** Windows 시스템 제어, 레지스트리 읽기, 로컬 앱 실행 등 PowerShell의 강력한 기능을 Agent의 Tool로 활용.

\#\# 🚀 Getting Started

\#\#\# Prerequisites

1\. **\*\*WSL2 Backend:\*\*** WSL2 환경에 OpenAI API 호환 LLM 서버가 실행 중이어야 합니다.  
   \`\`\`bash  
   \# WSL2 터미널 예시 (vLLM 구동)  
   python \-m vllm.entrypoints.openai.api\_server \--model Qwen/Qwen3-8B

2. **Windows Frontend:** Python 3.10 이상 권장.

## **Installation**

Windows PowerShell을 열고 아래 명령어를 순서대로 실행합니다.

PowerShell

\# 1\. Clone the repository  
git clone \[https://github.com/your\-org/SPAK\-WinCLI.git\](https://github.com/your\-org/SPAK\-WinCLI.git)  
cd SPAK\-WinCLI

\# 2\. Create a virtual environment & install dependencies  
python \-m venv venv  
.\\venv\\Scripts\\Activate  
pip install \-r requirements.txt

\# 3\. Setup Environment Variables  
cp .env.example .env  
\# .env 파일을 열어 WSL2 API 주소를 확인합니다. (기본값: http://localhost:8000/v1)

## **Usage**

작업을 수행할 로컬 폴더 경로와 실행할 Spec을 지정하여 에이전트를 구동합니다.

PowerShell

python core/agent\_loop.py \-\-spec specs/code\_review\_spec.yaml \-\-workspace C:\\Users\\jovyan\\Desktop\\TargetProject

## **📂 Directory Structure**

Plaintext

ohmy-agent/  
├── core/                   \# 에이전트 커널 및 실행 루프 로직  
│   ├── agent\_loop.py       \# 메인 ReAct 무한 루프  
│   ├── spec\_parser.py      \# AgentSpec 파싱 및 프롬프트 빌더  
│   └── memory.py           \# 단기/장기 메모리 관리 (상태 유지)  
├── tools/                  \# 에이전트가 호출할 수 있는 로컬 도구 모음  
│   ├── file\_system.py      \# 파일 읽기/쓰기/탐색  
│   └── shell\_executor.py   \# PowerShell 명령어 안전 실행  
├── specs/                  \# 에이전트 역할 및 목표 명세서 (AgentSpec DSL)  
│   ├── agent\_spec.yaml  
│   └── code\_review\_spec.yaml  
├── workspace/              \# 에이전트가 기본적으로 활동할 격리된 로컬 폴더  
├── spak.py                
├── requirements.txt  
└── README.md

## **🛡️ Security & Sandboxing**

* **주의:** 에이전트에게 시스템(PowerShell) 제어 권한을 부여하므로, 초기 테스트 시에는 파괴적인 명령어(rm, del 등) 실행을 제한하는 **Dry-run 모드**나 사용자 승인(Human-in-the-loop) 프롬프트를 활성화하는 것을 권장합니다.  
* 모든 파일 작업은 지정된 workspace 디렉토리 내부로 제한되도록 tools/file\_system.py에 경로 검증(Path Traversal 방지)이 구현되어야 합니다.

## **🤝 Contributing**

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

\---

이 README를 기반으로 프로젝트 뼈대를 잡으시면, 백엔드 인프라와 로컬 애플리케이션의 역할이 아주 명확하게 분리될 것입니다. 

다음 단계로, 위 디렉토리 구조에서 가장 핵심이 되는 \*\*\`core/agent\_loop.py\` (WSL2의 API를 호출하고 PowerShell 명령어를 실행하는 파이썬 무한 루프 뼈대 코드)\*\*를 바로 작성해 드릴까요?

## online 강의자료 용 Playbook 제작
### 핵심 요구사항
- online playbook 혹은 강의자료를 만드는 출판사가 사용할 agent system을 만든다고 할 때,
Agent와 SemanticStore 의 요구사항은 무엇일까?
- html은 lit component를 이용하여 만들고, vite run dev (?)를 이용해 만들어진 online playbook을 실행한다고 하자.
- BOOK 이라는 entity에 대한 정보를 yaml 혹은 md file로 저장한다고 하자. 제목과 목차
- 각 chapter는 다시 entity가 되고, 세부 정보를 저정하는 yaml 혹은 md file로 저장.
- BOOK은 chapter로 관계를 맺고 hyperlink로 연결되도록 SemanticStore가 지원해야 한다.
- streamlit run spak.py에 의해 열리는 web page는 무슨 정보를 표시해야 할까?
- User는 playboook을 검토하고, 수정이 필요한 사항을 md 파일로 작성하고, spak 제어판(?) 혹은 dashboard(?)에서 해당 md 파일을 upload하여 agent에게 작업 지시를 한다. 
- agent를 전체 task를 sub-tasks로 분해하고, 순차적으로 수정하되, 커다란 양의 content creation이 필요한 경우, gemini cli를 통해 필요한 html을 직접 생성하도록 한다. 
- agent는 web search를 통해 필요한 정보를 가져와 playbook 편집에 사용할 수 있다.
- spak 제어판에서는 진행 상황을 user가 볼 수 있어야 한다.
- SemanticStore는 Given-When-Then 형식으로 지식을 축적하고 검색하여 재활용할 수 있어야 한다.
- SemanticStore는 Key-Value 혹은 Entity Relation 관계를 표현할 수 있어야 한다.
- SemanticStore는 먼저 python 딕셔너리와 파일로 간단히 만들어 실험을 하다가 필요한 시점에 적절한 외부 library나 framework을 활용하는 것으로 전환한다.
# 🚀 AI 시스템 빌드 및 에이전트 개발 (ai-system-build)

## 🎓 수업 개요: 컴퓨터시스템빌드캡스톤디자인

- **수업 방식**: 3학년 5명씩 5개팀 구성하여 Project-Based 실습 수업으로 진행
- **담당 교수**: 김태원 (taewony@wsu.ac.kr)
- **핵심 목표**: 로컬 GPU 환경과 서버 환경을 모두 경험하며, 단순 LLM 활용을 넘어 자율적인 **AI Agent**를 설계하고 **Gradio** 혹은 **FastAPI** 기반의 웹 서비스로 구현하는 실전 역량을 배양합니다.
- **사전 준비**: 수업은 W15 강의실 107에서 화목금 4시간씩 4주간 진행됩니다. 자기 PC 자리를 미리 확보하여 ollama를 설치하고, `00_ollama_basic` 예시 코드를 실행해 보세요.
- **문의 사항**: email(taewony@wsu.ac.kr) 또는 W17 505호 연구실 방문.

---

### 📚 주요 교재 및 참고 도서

- 📘 **올라마와 오픈소스 LLM을 활용한 AI 에이전트 개발 입문** (위키북스)
- 📗 **AI 에이전트 엔지니어링** (한빛미디어)

---

### 💻 개발 환경 및 프로젝트 구성

수업은 총 5개 팀으로 나뉘어 진행되며, 하드웨어 환경에 따라 두 가지 트랙으로 운영됩니다.

#### [Track 1] GPU 서버 트랙 (2개 팀: Project #1, #2)

- **환경**: Ubuntu Linux 서버 + NVIDIA L40S (48GB VRAM)
- **핵심 기술**: vLLM, Kubernetes, Kserve, Gradio
- **목표**: 고성능 서버 환경에서 대규모 모델(Qwen3-30B 등) 서빙 및 멀티 유저 서비스 구축.

#### [Track 2] 로컬 PC 트랙 (3개 팀: Project #3, #4, #5)

- **환경**: Windows 11 + VS Code + **NVIDIA RTX 4070** (WSL2 활용)
- **핵심 기술**: **Ollama**, **Anthropic Messages API**, **FastAPI / Gradio**, **Python Agent Programming**
- **목표**: 로컬 GPU 성능을 극대화하여 Ollama 기반 자율 에이전트를 개발하고 웹 서비스로 상용화 수준까지 구축.

---

### 🛠️ 실습 및 프로젝트 상세 (Local PC Track 중심)

#### 1. Ollama 기초 및 표준 API 학습 (`00_ollama_basic`)

- Ollama 설치 및 로컬 모델(`qwen2.5:7b` 등) 최적화.
- OpenAI 및 Anthropic SDK 표준 호환 레이어를 이용한 통신 기법 습득.
- **RAG** 기초: 인메모리 벡터 검색 구현.

#### 2. 에이전트 루프 및 도구 연동 (`01_weather_agent`)

- **생각 -> 행동 -> 관찰** 루프 설계.
- 위치 정보 및 날씨 API 등 외부 도구 연동.

#### 3. 지능형 코칭 에이전트 (TUI) (`02_coaching_agent`)

- **Gap Analysis**: 현재와 목표 사이의 간극을 분석하는 논리 모델 구축.
- **Anthropic Messages API**를 활용한 복잡한 추론 워크플로우 설계.
- **Terminal UI**: 터미널 환경에서 대화 맥락을 유지하며 동작하는 코칭 봇 구현.

#### 4. 웹 기반 에이전트 서비스 (`03_web_based_agent_service`)

- **Web Stack 선택**: **FastAPI** (백엔드 중심) 또는 **Gradio** (UI 중심) 중 팀별 선택.
- **서비스화**: 개발된 에이전트 로직을 웹 API/UI로 노출하여 실제 사용 가능한 애플리케이션으로 변환.

---

### 🤝 멘토링 및 협업

- **외부 멘토**: 스타셀 박노헌 대표 (GPU 서버 활용 및 실무 AI 서비스 아키텍처 멘토링)
- **수업 진행**: 실습 위주의 워크숍 형태와 팀별 자율 프로젝트 병행.

---

# ai-system-build

## <<컴퓨터시스템빌드캡스톤디자인 수업 개요>>

- 2026학년도 1학기 3학년 (수강인원 24명, 첫수업은 5월 26일 화요일)
- 김태원 (taewony@wsu.ac.kr)

### 참고도서 혹은 교재 :

- 올라마와 오픈소스 LLM을 활용한 AI 에이전트 개발 입문 - 서영배 외 지음 (출판사 위키북스)
- AI 에이전트 엔지니어링 (단일 에이전트부터 멀티 에이전트 시스템까지, AI 앱 개발 올인원 가이드, 한빛미디어)
-

### 개발환경 :

- GPU 서버 (Ubuntu linux) : Project #1 & #2
- Windows VS code and RTX4070 (with WSL linux): Project #3, #4, #5

### 팀별프로젝트 계획

- nvidia-smi 실행을 위해 NVIDIA tool-kit 설치, WSL linux 설치
- 우선 Ollama를 windows PC에 설치하고, python 환경에서 API 호출하며 LLM service를 사용해 본다.
- PyTorch를 사용해 matmul 연산 및 autograd 함수 이용해 간단한 기계학습 예제 코드 실행해 본다.
- LLM을 활용하는 application을 파이썬으로 기획하고 개발하는 프로젝트를 팀 구성해서 수행한다.
- 2개팀은 GPU Linux 서버 및 L40S GPU를 사용한 Project #1, #2를 수행.
- 나머지 3개팀은 Windows 환경에서 RTX5070을 사용해 local LLM을 활용한 application 개발 프로젝트 수행
- 스타셀 박노헌 대표께서 GPU 서버 활용 프로젝트 수행에 대해 멘토링해 주심 (2회 대면, 1회 비대면)

### Project #1 :

#### GPU서버 및 Ollama 활용 single-user LLM service 구축

- Ollama 설치 및 적당한 model download
- Local LLM 호출하여 chatting 서비스를 제공하는 web server 구축...
- 외부 PC에서 GPU서버 IP 주소로 접속하면 chatting web service 시작

#### 사용 환경 : 필요에 따라 변경

GPU 서버의 Kubeflow Notebook(가상시스템)
GPU : L40s 1개 할당(Memory 48GB)
CPU : 16 core
RAM : 64GB
Storage : 500GB

#### 프로젝트 과제

1. Ollama 설치와 세팅
   할당된 가상시스템(Linux 환경)에 Ollama를 설치하고 세팅 및 테스트
2. Jupyterlab환경에서 Python으로 API를 이용하여 Ollama Server에 접속하여 LLM 기능 구현
3. gradio를 이용하여 챗봇 기능의 AI Agent 개발

#### 사용 절차

1. Ollama 설치
2. LLM Model 선택 : qwen3:8b부터 시작, Qwen3-30B-A3B-Instruct-2507-FP8 사용 가능, 다른 모델로 변경 가능
3. 모델 준비 : Ollama setting
4. Agent 개발 : gradio 사용(python coding)

#### 추가 개발 : RAG(Retrieval-Augmented Generation) 개발

1. Vector Store 구축 : faiss 사용
2. vector data 저장
   문서 청킹
   토큰화
   임베딩
3. gradio를 이용한 RAG AI Agent 개발
   검색 기능 사용
   문서 검색 후 LLM 활용하여 문장 생성

### Project #2 :

#### GPU서버 및 vLLM을 이용한 multi-user LLM service 구축..

사용 환경: 필요에 따라 변경
GPU 서버의 Kubeflow Notebook(가상시스템)
GPU : L40s 1개 할당(Memory 48GB)
CPU : 16 core
RAM : 64GB
Storage : 500GB

#### 프로젝트 과제

1. 가상시스템 환경에서 vLLM을 설치하고 LLM서비스를 제공
2. Kubernetes와 Kserve 기능을 활용하여 LLM서비스를 제공
3. 구축된 LLM서비스를 이용한 AI Agent 개발

#### 사용 절차

1. 가상시스템에 vLLM설치
2. LLM Model을 선택하여 설치
3. LLM Model 서비스를 구축
4. LLM Model 서비스에 접속하여 문장 생성과 질의응답 테스트
5. Kserve를 이용하여 LLM 서비스 구축
6. 외부 시스템에서 LLM 서비스를 구축할 수 있도록 설정
7. 외부에서 LLM 서비스에 구축하여 사용
8. gradio를 이용하여 AI Agent 개발

---

_최종 수정일: 2026년 2월 26일_

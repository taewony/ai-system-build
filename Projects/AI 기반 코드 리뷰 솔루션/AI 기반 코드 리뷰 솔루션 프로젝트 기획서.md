# **🚀 AI 기반 코드 리뷰 솔루션 (Capstone Design)**

본 프로젝트는 GitHub Pull Request(PR) 프로세스의 효율성을 극대화하기 위해 AI를 활용한 **자동 리뷰 및 상세 주석 생성 시스템**을 구축하고, 하드웨어 및 언어모델별 성능 차이를 비교 분석하는 엔지니어링을 목표로 합니다.

## **1\. 프로젝트 개요**

* **핵심 아이디어**: GitHub PR 분석을 통한 요약, 자동 코멘트, 및 사용자가 선택한 단위(Line/Function/File)별 상세 리뷰 제공.  
* **차별점**: 단순 요약을 넘어 개발자가 원하는 수준의 **Granular Control(세밀한 제어)** 기능을 제공하며, 로컬 sLM과 상용 LLM의 성능/비용/보안 지표를 대조하여 최적의 아키텍처를 제시함.

## **2\. 시스템 검증 및 성능 지표 (KPI)**

성공적인 프로젝트 완수를 위해 시스템의 Pass/Fail 기준과 측정 가능한 지표를 정의합니다.

### **2.1 Pass/Fail 정의**

* **기능적 Pass**:  
  * GitHub Webhook 수신 후 1분 이내에 코멘트가 PR에 정상 등록됨.  
  * 선택된 단위(라인/함수/파일)에 맞는 주석이 정확한 위치에 생성됨.  
* **품질적 Pass**:  
  * AI가 제안한 코드 수정안 중 70% 이상이 문법적으로 오류가 없음.  
  * Hallucination(환각)을 통해 존재하지 않는 변수나 함수를 언급하는 빈도가 10% 미만임.

### **2.2 핵심 측정 지표**

1. **응답 시간 (Latency)**: Webhook 수신 시점부터 GitHub API 응답 완료 시점까지의 시간 (TTFT 포함).  
2. **처리량 (Throughput)**: 단위 시간당 처리 가능한 PR 수 (L40S 서버 환경에서 병렬 처리 성능 측정).  
3. **토큰 소모량 (Token Usage)**: PR당 평균 입력/출력 토큰량 측정 (비용 효율성 분석).  
4. **리뷰 정확도 (Precision)**: Gemini CLI로 생성된 Ground Truth 대비 AI 리뷰의 유사도 점수.

## **3\. 단계별 로드맵 (Milestones)**

### **📍 Phase 1: Local Prototype & Baseline (1\~4주차)**

**목표: 로컬 PC(RTX 4070\) 기반의 핵심 로직 검증**

* **환경 구축**: PC(RTX 4070)에 Ollama/vLLM 설치 및 DeepSeek-Coder-7B 구동.  
* **테스트 케이스 생성**: Gemini CLI를 사용하여 버그, 성능 이슈, 스타일 위반이 포함된 50개 이상의 diff 샘플 생성.  
* **실험 1 (Local sLM)**: PC 환경에서 로컬 모델의 속도와 품질 측정.  
* **실험 2 (Cloud LLM)**: 동일 케이스를 OpenAI(GPT-4o)로 실행하여 sLM과의 성능 격차 확인.

### **📍 Phase 2: Integration & Server Expansion (5\~10주차)**

**목표: 실제 GitHub 연동 및 고성능 서버 환경 확장**

* **서버 구축**: FastAPI 기반 백엔드 서버 구축 및 GitHub Webhook 연동.  
* **인프라 확장**: Linux 서버(L40S GPU) 환경으로 이전.  
* **실험 3 (Server sLM)**: L40S 환경에서 모델의 정밀도(FP16)를 높이고 Batch Inference를 통한 처리량 증대 실험.  
* **실험 4 (Server LLM)**: 서버에서 클라우드 API 호출 시의 전체 시스템 레이턴시 비교 분석.

### **📍 Phase 3: RAG 도입 및 최적화 (11\~15주차)**

**목표: 팀 맞춤형 리뷰(RAG) 구현 및 최종 평가**

* **RAG 시스템 구현**:  
  * 프로젝트 내 기존 코드 스타일 가이드와 과거 리뷰 데이터를 벡터 DB(ChromaDB/SQLite)에 저장.  
  * 리뷰 생성 시 관련 컨텍스트를 검색하여 Prompt에 주입 (팀 특화 코멘트 생성).  
* **최종 벤치마킹**: 4가지 환경(PC sLM, PC LLM, Server sLM, Server LLM)의 지표를 통합 분석.  
* **결과 시각화**: 환경별 가성비(성능 대비 비용) 및 보안성 매트릭스 도출.

## **4\. 환경별 비교 매트릭스 설계**

본 프로젝트는 아래 4가지 환경의 데이터를 수집하여 최종 보고서의 핵심 근거로 활용합니다.

| 환경 ID | H/W 자원 | 모델 (S/W) | 강점 | 약점 |
| :---- | :---- | :---- | :---- | :---- |
| **Env 1** | PC (RTX 4070\) | DeepSeek (sLM) | 보안성, 비용 제로 | 낮은 처리량, 모델 정밀도 한계 |
| **Env 2** | PC (RTX 4070\) | GPT-4o (LLM) | 높은 리뷰 품질 | 데이터 유출 위험, API 비용 발생 |
| **Env 3** | Server (L40S) | DeepSeek (sLM) | 압도적 처리량, 고정밀도 | 서버 유지 비용 및 관리 난이도 |
| **Env 4** | Server (L40S) | GPT-4o (LLM) | 최상급 리뷰 품질 | 네트워크 레이턴시 영향 |

## **5\. 학생 가이드: 테스트 자동화 팁**

1. **Gemini CLI 활용**: 테스트 케이스 생성 시 "이 코드를 수정하고 싶게 만드는 버그 3개를 포함해줘"와 같은 페르소나를 부여하여 다양한 변별력을 가진 데이터를 확보하세요.  
2. **NAT 환경 대응**: PC가 내부 망에 있을 경우 ngrok을 사용하여 외부 GitHub Webhook이 로컬 FastAPI 서버에 도달할 수 있도록 설정하세요.  
3. **로그 기록**: 모든 실험 결과는 JSON 형태로 저장하여 나중에 Pandas/Matplotlib으로 그래프를 그릴 수 있게 준비하세요.

본 기획서는 단순히 기능을 '만드는' 것을 넘어, 어떤 환경에서 AI가 가장 효율적으로 동작하는지 '증명'하는 데 초점이 맞춰져 있습니다. L40S 서버와 RTX 4070 간의 성능 차이를 수치로 보여준다면 매우 수준 높은 캡스톤 프로젝트가 될 것입니다.

---

## 참고 #1
Cloud LLM(OpenAI 등)만 사용한다면 서버의 GPU 성능은 큰 의미가 없습니다. 서버의 CPU 만으로 서비스 제공이 가능합니다.

* **Cloud LLM 사용 시**: L40S는 거의 놀게 됩니다. 이때 서버는 단순한 **Network Gateway** 역할만 수행합니다.  
* **Local sLM 사용 시**: L40S는 RTX 4070에서 구동하기 힘들었던 **고정밀도(FP16) 모델**이나 **대용량 파라미터(30B 이상) 모델**을 돌릴 수 있게 해주는 **핵심 엔진**이 됩니다. 

---

## 참고 #2 **🛠️ 환경 이전 및 가상환경 설정 가이드 (PC to Server)**

본 가이드는 Windows 개발 환경에서 작성한 코드를 Linux(Ubuntu) GPU 서버로 옮길 때 발생하는 '환경 파편화' 문제를 해결하기 위한 표준 절차를 안내합니다.

---

## **2\. 파이썬 가상환경 설정 및 이식성 전략**

학생들이 가장 흔히 하는 실수는 Windows에서 설치한 라이브러리 폴더(venv)를 그대로 서버에 복사하는 것입니다. 이는 절대 작동하지 않습니다. 대신 아래의 **"Freeze & Install"** 방식을 사용해야 합니다.

### **Step 1: PC(Windows)에서 환경 내보내기**

개발이 완료된 시점에 사용 중인 라이브러리 목록을 추출합니다.

```Bash
# 가상환경 활성화 상태에서 실행

pip freeze \> requirements.txt
```

### **Step 2: 서버(Linux)에서 환경 재구축**

서버(Ubuntu 24.04 등)에 접속하여 새로운 가상환경을 만들고 설치합니다.

```Bash

# 1\. 저장소 복제 (Git 사용 권장)

git clone \<your-repo-url\>
cd \<project-folder\>

# 2\. 가상환경 생성

python3 \-m venv venv

# 3\. 가상환경 활성화

source venv/bin/activate

# 4\. 라이브러리 일괄 설치

pip install \--upgrade pip
pip install \-r requirements.txt
```

---

## **3\. GPU 가속을 위한 핵심 팁 (PyTorch & CUDA)**

Windows PC와 Linux 서버는 GPU 드라이버와 CUDA 버전이 다를 수 있습니다. requirements.txt에 torch가 포함되어 있더라도, GPU 서버에서는 해당 환경의 CUDA 버전에 맞는 명령어로 재설치하는 것이 안전합니다.

* **추천 방식**: [PyTorch 공식 사이트](https://pytorch.org/get-started/locally/)에서 서버의 CUDA 버전(예: 12.1 또는 12.4)에 맞는 설치 명령어를 복사해 실행하도록 가이드하세요.  

``Bash

\# 예시: CUDA 12.1용 PyTorch 설치

pip install torch torchvision torchaudio \--index-url https://download.pytorch.org/whl/cu121

*   
* 

---

## **4\. 더 높은 수준의 이식성: Docker 활용 (권장)**

만약 학생들이 조금 더 실무적인 방식을 배우길 원한다면, **Docker** 사용을 강력히 추천합니다.

1. **PC에서**: Dockerfile을 작성하여 환경을 이미지화합니다.  
2. **서버에서**: docker pull로 이미지를 가져와 실행합니다.  
   * 이 방식은 GPU 드라이버 충돌 문제를 NVIDIA Container Toolkit이 해결해주므로 환경 이전에 따른 스트레스가 거의 없습니다.

---


## **📋 PC에서 GPU 서버로 환경 이전하기**

프로젝트의 연속성을 위해 반드시 아래 절차를 준수하여 환경을 설정하세요.

### **1\. 파이썬 버전 통일 (중요)**

* **권장 버전**: Python 3.12.x
* **이유**: GPU 서버(Ubuntu 24.04)의 기본 파이썬 버전이 3.12입니다. 개발 PC와 서버의 버전을 일치시켜야 라이브러리 의존성 꼬임(Dependency Hell)을 방지할 수 있습니다.
* **PC 설정 팁**: Windows 사용자는 python.org에서 3.12 버전을 직접 설치하거나, pyenv-win 또는 Conda를 사용하여 버전을 서버와 동일하게 맞추는 것이 좋습니다.

### **2\. 가상환경 관리 (venv)**

* **절대 금지**: Windows의 venv 폴더를 서버로 직접 복사하지 마세요.  
* **방법**:  
  1. PC에서 pip freeze \> requirements.txt 실행  
  2. 서버에서 python3 \-m venv venv로 새 환경 생성  
  3. pip install \-r requirements.txt로 재설치

### **3\. 환경 변수 관리 (.env)**

* API Key(OpenAI, GitHub Token) 및 DB 경로는 절대 코드에 하드코딩하지 않습니다.  
* .env 파일을 만들어 관리하고, 서버 이동 시 이 파일만 따로 복사하거나 직접 생성하세요.  
```
* OPENAI\_API\_KEY=your\_key\_here  
* GITHUB\_TOKEN=your\_token\_here  
* DATABASE\_URL=sqlite:///./app.db  
* MODEL\_PATH=/models/deepseek-7b  \# 서버의 GPU 모델 경로  
```

### **4\. GPU 서버(L40S) 최적화 설정**

* L40S의 대용량 VRAM(48GB)을 활용하려면 vLLM 라이브러리 사용 시 gpu\_memory\_utilization 설정을 0.9 정도로 높게 잡아 처리량을 극대화하세요.  
* Linux 서버에서는 screen 또는 tmux를 사용하여 터미널 연결이 끊어져도 서버 프로세스가 유지되도록 하세요.


# ai-system-build

<<컴퓨터시스템빌드캡스톤디자인 수업 개요>>
- 2026학년도 1학기 3학년 (수강인원 24명, 첫수업은 5월 26일 화요일)

- 개발환경 :
  . GPU 서버 (Ubuntu linux) : Project #1 & #2
  . Windows VS code and RTX4070 (with WSL linux): Project #3, #4, $5

- 팀별프로젝트 계획
  . nvidia-smi 실행을 위해 NVIDIA tool-kit 설치, WSL linux 설치
  . 우선 Ollama를 windows PC에 설치하고, python 환경에서 API 호출하며 LLM service를 사용해 본다.
  . PyTorch를 사용해 matmul 연산 및 autograd 함수 이용해 간단한 기계학습 예제 코드 실행해 본다.
  . LLM을 활용하는 application을 파이썬으로 기획하고 개발하는 프로젝트를 팀 구성해서 수행한다. 
  . 2개팀은 GPU Linux 서버 및 L40S GPU를 사용한 Project #1, #2를 수행. 
  . 나머지 3개팀은 Windows 환경에서 RTX5070을 사용해 local LLM을 활용한 application 개발 프로젝트 수행
  . 스타셀 박노헌 대표께서 GPU 서버 활용 프로젝트 수행에 대해 멘토링해 주심 (2회 대면, 1회 비대면)

Project #1 : 
  GPU서버 및 Ollama 활용 single-user LLM service 구축
  - Ollama 설치 및 적당한 model download
  - Local LLM 호출하여 chatting 서비스를 제공하는 web server 구축...
  - 외부 PC에서 GPU서버 IP 주소로 접속하면 chatting web service 시작

사용 환경 : 필요에 따라 변경
  GPU 서버의 Kubeflow Notebook(가상시스템)
  GPU : L40s 1개 할당(Memory 48GB)
  CPU : 16 core
  RAM : 64GB
  Storage : 500GB

프로젝트 과제
  1. Ollama 설치와 세팅
    할당된 가상시스템(Linux 환경)에 Ollama를 설치하고 세팅 및 테스트
  2. Jupyterlab환경에서 Python으로 API를 이용하여 Ollama Server에 접속하여 LLM 기능 구현
  3. gradio를 이용하여 챗봇 기능의 AI Agent 개발

사용 절차
  1. Ollama 설치
  2. LLM Model 선택 : qwen3:8b부터 시작, Qwen3-30B-A3B-Instruct-2507-FP8 사용 가능, 다른 모델로 변경 가능
  3. 모델 준비 : Ollama setting
  4. Agent 개발 : gradio 사용(python coding)

추가 개발 :   RAG(Retrieval-Augmented Generation) 개발
  1. Vector Store 구축 : faiss 사용
  2. vector data 저장
    문서 청킹
    토큰화
    임베딩
  3. gradio를 이용한 RAG AI Agent 개발
    검색 기능 사용
    문서 검색 후 LLM 활용하여 문장 생성



Project #2 : 
  GPU서버 및 vLLM을 이용한 multi-user LLM service 구축..

사용 환경: 필요에 따라 변경
  GPU 서버의 Kubeflow Notebook(가상시스템)
  GPU : L40s 1개 할당(Memory 48GB)
  CPU : 16 core
  RAM : 64GB
  Storage : 500GB

프로젝트 과제
  1. 가상시스템 환경에서 vLLM을 설치하고 LLM서비스를 제공
  2. Kubernetes와 Kserve 기능을 활용하여 LLM서비스를 제공
  3. 구축된 LLM서비스를 이용한 AI Agent 개발

사용 절차
  1. 가상시스템에 vLLM설치
  2. LLM Model을 선택하여 설치
  3. LLM Model 서비스를 구축
  4. LLM Model 서비스에 접속하여 문장 생성과 질의응답 테스트
  5. Kserve를 이용하여 LLM 서비스 구축
  6. 외부 시스템에서 LLM 서비스를 구축할 수 있도록 설정
  8. 외부에서 LLM 서비스에 구축하여 사용
  9. gradio를 이용하여 AI Agent 개발

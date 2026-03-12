# Nano-vLLM Gradio Agent Service 구축 계획서 (api-server-plan.md)

이 문서는 `nano-vllm`을 기반으로 **Gradio**를 활용하여 누구나 쉽게 접속해 사용할 수 있는 초간단 Agent 웹 서비스를 구축하기 위한 계획을 담고 있습니다.

## 1. 프로젝트 개요
*   **목적**: `nano-vllm`의 추론 엔진을 Gradio의 `ChatInterface`와 결합하여, 복잡한 API 설정 없이 즉시 대화 및 도구 사용(Tool Use)이 가능한 Agent 데모 구축.
*   **핵심 가치**: 
    *   **초간단 구현**: FastAPI 대비 훨씬 적은 코드로 UI와 연동.
    *   **인터랙티브 UI**: 별도의 프론트엔드 개발 없이 채팅 UI, 로그 출력, 파라미터 조절 기능 제공.
    *   **실시간 스트리밍**: Gradio의 Generator 지원을 통한 자연스러운 응답 출력.

## 2. 기술 스택
*   **Inference Engine**: `nano-vllm` (Qwen3-8B)
*   **UI Framework**: Gradio (ChatInterface 중심)
*   **Agent Logic**: Simple ReAct Pattern (Thought -> Action -> Observation -> Response)
*   **Concurrency**: Gradio 내장 Queue 시스템

## 3. 단계별 구현 계획

### Phase 1: Gradio 기초 챗봇 연동
*   **목표**: `nano-vllm`과 Gradio `ChatInterface`를 연결하여 기본 대화 기능 구현.
*   **주요 작업**:
    *   `nano-vllm` 로드 및 초기화 코드 작성.
    *   Gradio `gr.ChatInterface`를 활용한 기본 UI 구성.
    *   `example.py`의 추론 로직을 Gradio의 `predict` 함수로 래핑.

### Phase 2: 실시간 스트리밍 지원
*   **목표**: 토큰이 생성되는 대로 UI에 즉시 표시.
*   **주요 작업**:
    *   `nano-vllm`의 스트리밍 출력 기능을 활용하여 Python `yield` 문으로 응답 생성.
    *   Gradio의 비동기/제너레이터 지원을 통한 부드러운 텍스트 렌더링.

### Phase 3: 도구 사용(Tool Use) Agent 구현
*   **목표**: 모델이 특정 키워드나 형식을 출력하면 외부 함수(계산기, 검색 등)를 실행하고 결과를 다시 입력으로 넣는 루프 구현.
*   **주요 작업**:
    *   `Simple Tools`: 계산기(`eval`), 현재 시간 출력 등 기초 도구 정의.
    *   `ReAct Loop`: 모델이 "Action: [tool_name]"을 출력하면 멈추고, 도구를 실행한 뒤 "Observation: [result]"를 덧붙여 다시 추론 요청.
    *   UI 상에 Agent의 '생각(Thought)' 과정 표시 여부 결정.

### Phase 4: 멀티 유저 큐 및 배칭 (선택 사항)
*   **목표**: 다수의 사용자가 접속했을 때 효율적인 처리.
*   **주요 작업**:
    *   Gradio `queue()` 설정을 통한 요청 순차 처리 보장.
    *   (고급) `gr.batch` 기능을 활용하여 여러 유저의 요청을 `nano-vllm`의 배치 추론으로 연결.

## 4. 핵심 코드 구조 설계

### Directory Structure
```text
nano-vllm-gradio/
├── app.py               # Gradio 메인 실행 파일
├── engine.py            # nano-vllm 관리 클래스
├── agent.py             # ReAct 루프 및 도구 실행 로직
└── requirements.txt
```

### Gradio Agent 루프 개념 (Pseudocode)
```python
import gradio as gr
from engine import NanoVLLMEngine

engine = NanoVLLMEngine()

def agent_respond(message, history):
    # 1. 이전 대화 이력과 결합하여 프롬프트 생성
    prompt = f"System: You are a helpful agent with tools...\nUser: {message}"
    
    # 2. ReAct 루프 시작
    full_response = ""
    for token in engine.generate_stream(prompt):
        full_response += token
        yield full_response  # 실시간 업데이트
        
    # 3. 도구 호출 확인 (예: 'Action: calculator[5+5]')
    if "Action:" in full_response:
        # 도구 실행 및 추가 추론 로직 (중략)
        pass
```

## 5. 검증 및 테스트 계획
1.  **UI 확인**: 웹 브라우저에서 채팅창이 정상적으로 뜨고 입력이 가능한지 확인.
2.  **스트리밍 확인**: 한 글자씩 타이핑되듯 응답이 오는지 확인.
3.  **Agent 기능 확인**: "123 * 456이 뭐야?" 같은 질문에 계산기 도구를 사용하는지 확인.

## 6. 기대 효과
*   **속도**: 최소한의 코드로 동작하는 Agent 프로토타입 확보.
*   **시각화**: 모델의 추론 과정을 눈으로 직접 보며 튜닝 가능.
*   **데모**: URL 공유 기능을 통해 외부에서도 내 GPU 서버의 기능을 테스트 가능.

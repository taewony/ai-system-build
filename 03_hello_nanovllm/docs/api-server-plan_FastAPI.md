# Nano-vLLM API Server 구축 계획서 (api-server-plan_FastAPI.md)

이 문서는 `nano-vllm`을 기반으로 OpenAI 호환 API 및 Agent 서비스를 제공하는 웹 서버를 구축하기 위한 구체적인 실행 계획을 담고 있습니다.

## 1. 프로젝트 개요
*   **목적**: `nano-vllm`의 효율적인 추론 능력을 네트워크를 통해 멀티 유저에게 제공하고, 단순 추론을 넘어 도구 사용(Tool Use)이 가능한 Agent 서비스로 확장.
*   **핵심 가치**: 
    *   **OpenAI 호환성**: 기존 OpenAI SDK를 사용하는 클라이언트와 즉시 연동.
    *   **비동기 처리**: FastAPI와 asyncio를 활용한 효율적인 I/O 처리.
    *   **동적 배치(Dynamic Batching)**: 여러 사용자 요청을 하나로 묶어 GPU 효율 극대화.

## 2. 기술 스택
*   **Inference Engine**: `nano-vllm` (Qwen3-8B 모델 기반)
*   **Web Framework**: FastAPI (Python 기반 고성능 웹 프레임워크)
*   **Asynchronous Runtime**: `asyncio` & `uvicorn`
*   **Data Validation**: `pydantic` (OpenAI API 스키마 정의)
*   **Agent Logic**: Custom prompt-based ReAct or Tool-use logic

## 3. 단계별 구현 계획

### Phase 1: 기초 API 서버 및 OpenAI 호환성 확보
*   **목표**: 단일 유저 대상의 `/v1/chat/completions` API 구현 (Non-streaming).
*   **주요 작업**:
    *   `FastAPI` 기본 구조 설정.
    *   OpenAI 요청/응답 스키마 (`ChatCompletionRequest`, `ChatCompletionResponse`) 정의.
    *   `nano-vllm`을 로드하고 관리하는 `EngineWrapper` 클래스 생성.
    *   `example.py`의 로직을 API 핸들러에 이식.

### Phase 2: 비동기 엔진 래퍼 및 스트리밍 지원
*   **목표**: SSE(Server-Sent Events)를 통한 실시간 토큰 생성 및 비동기 엔진 구현.
*   **주요 작업**:
    *   `nano-vllm`의 `generate`를 비동기적으로 실행하기 위한 `AsyncEngine` 래퍼 구현 (ThreadPoolExecutor 활용 고려).
    *   `StreamingResponse`를 활용한 토큰 단위 응답 처리.
    *   Chat Template (Qwen3) 적용 자동화.

### Phase 3: 멀티 유저 요청 스케줄러 (Dynamic Batching)
*   **목표**: 여러 유저의 요청을 큐(Queue)에 쌓고, 일정 주기 또는 크기로 묶어 `nano-vllm`에 전달.
*   **주요 작업**:
    *   `asyncio.Queue`를 이용한 Request Queue 구현.
    *   Background Worker: 큐에서 요청을 꺼내 배치를 구성하고 엔진에 전달하는 루프 구현.
    *   결과를 각 요청자에게 돌려주기 위한 `asyncio.Future` 또는 `Event` 관리.

### Phase 4: 세션 메모리 및 Agent 기능 (Tool Use)
*   **목표**: 대화 이력 유지 및 간단한 도구(계산기, 검색 등) 사용 기능 추가.
*   **주요 작업**:
    *   `In-memory Session Store`: `session_id`별로 `messages` 리스트 관리.
    *   `Agent Runtime`: 모델의 출력을 파싱하여 Tool Call을 감지하고 실행하는 루프 구현.
    *   System Prompt를 통한 Agent 페르소나 부여.

## 4. 핵심 코드 구조 설계

### Directory Structure
```text
nano-vllm-server/
├── app/
│   ├── main.py              # FastAPI 진입점
│   ├── core/
│   │   ├── engine.py        # nano-vllm 비동기 래퍼
│   │   └── scheduler.py     # Batching 스케줄러
│   ├── api/
│   │   ├── routes.py        # OpenAI 호환 엔드포인트
│   │   └── schema.py        # Pydantic 모델
│   └── agent/
│       ├── runtime.py       # Agent 추론 및 도구 실행 로직
│       └── tools.py         # 가용 도구 정의
├── config.py                # 모델 경로 및 환경 설정
└── requirements.txt
```

### Async Batching Scheduler 개념 (Pseudocode)
```python
class BatchScheduler:
    def __init__(self, engine):
        self.queue = asyncio.Queue()
        self.engine = engine
        
    async def add_request(self, prompt, params):
        future = asyncio.get_event_loop().create_future()
        await self.queue.put((prompt, params, future))
        return await future

    async def worker(self):
        while True:
            # 큐에서 최대 N개의 요청을 모음
            batch_reqs = []
            while len(batch_reqs) < MAX_BATCH_SIZE:
                req = await self.queue.get()
                batch_reqs.append(req)
                if self.queue.empty(): break
            
            # nano-vllm으로 일괄 추론
            prompts = [r[0] for r in batch_reqs]
            results = await self.engine.generate(prompts)
            
            # 결과 배분
            for (p, par, fut), res in zip(batch_reqs, results):
                fut.set_result(res)
```

## 5. 검증 및 테스트 계획
1.  **Unit Test**: `nano-vllm` 래퍼가 정상적으로 결과를 반환하는지 확인.
2.  **API Test**: `curl` 또는 `Postman`을 사용하여 OpenAI 규격 응답 확인.
3.  **Concurrency Test**: 다수의 동시 요청 시 스케줄러가 배치를 형성하여 처리하는지 로그 분석.
4.  **Agent Test**: 특정 도구 호출이 필요한 질문을 던져 ReAct 루프 작동 확인.

## 6. 기대 효과
*   **학습**: vLLM의 내부 구조와 실제 서빙 아키텍처의 연동 원리 깊이 이해.
*   **활용**: 나만의 경량화된 GPU 서버용 Agent API 구축.
*   **확장**: 향후 RAG(Retrieval-Augmented Generation) 시스템으로의 손쉬운 확장 기반 마련.

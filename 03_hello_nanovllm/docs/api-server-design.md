**nano-vLLM**은 약 **1,200줄 수준의 Python 코드로 구성된 경량 LLM inference 엔진**이라 구조를 이해하고 확장하기에 매우 좋습니다.

따라서 캡스톤 프로젝트에서 **multi-user agent service + OpenAI compatible API**를 구현하는 것은 매우 좋은 방향입니다.

아래는 **nano-vLLM 기반 multi-user Agent API Server 전체 설계**입니다.

---

## 1. 목표 시스템

### 목표

nano-vLLM 기반으로 다음 기능을 제공

* multi-user inference
* OpenAI API compatible
* agent execution
* streaming
* session memory
* tool use

즉 이런 구조입니다.

```
Clients
 (browser / app)
       │
       ▼
API Server (api-server.py)
       │
       ├── Auth
       ├── Session Manager
       ├── Agent Runtime
       ├── Request Scheduler
       │
       ▼
nano-vLLM Engine
       │
       ▼
GPU
```

---

## 2. 핵심 설계 철학

nano-vLLM은 원래 **offline batch inference 엔진**입니다.
그래서 API server를 만들 때 다음 3개를 추가해야 합니다.

### 반드시 필요한 3개

- Request queue
- Session memory
- OpenAI API wrapper

---

## 3️. 전체 컴포넌트 설계

## 시스템 구성

```
api-server.py
│
├── server
│   └── FastAPI app
│
├── auth
│   └── API key
│
├── session
│   └── user conversation state
│
├── agent
│   └── tool calling
│
├── scheduler
│   └── batching
│
└── engine
    └── nano-vllm wrapper
```

---

## 4. API compatibility 설계

OpenAI API와 호환되도록 다음 endpoint를 구현합니다.

### models

```
GET /v1/models
```

response

```
{
 "data":[
   {
     "id":"qwen3-8b",
     "object":"model"
   }
 ]
}
```

---

### chat completion

```
POST /v1/chat/completions
```

request

```
{
 "model":"qwen3-8b",
 "messages":[
   {"role":"user","content":"hello"}
 ],
 "temperature":0.7,
 "stream":true
}
```

---

### completion

```
POST /v1/completions
```

---


## 5. nano-vLLM engine wrapper

nano-vLLM 기본 사용 방식

```python
from nanovllm import LLM, SamplingParams

llm = LLM(model_path)

outputs = llm.generate(prompts, params)
```

그래서 wrapper를 만듭니다.

```
engine/
   nanovllm_engine.py
```

구조

```
NanoVLLMEngine
 ├ load_model()
 ├ generate()
 ├ generate_stream()
 └ batch_generate()
```

---

## 6. Request scheduler (핵심)

multi-user 시스템에서 가장 중요한 부분입니다.

```
scheduler/
   request_queue.py
```

구조

```
User Request
    │
    ▼
Queue
    │
Batch builder
    │
    ▼
nano-vLLM.generate()
```

예

```
req1
req2
req3
req4

→ batch
```

---

## 7. Session manager

multi-user agent 서비스를 위해 필요합니다.

```
session/
   session_store.py
```

구조

```
Session
 ├ user_id
 ├ conversation_history
 ├ tool_state
 └ metadata
```

---

## 8. Agent runtime

여기서 **agent 기능**을 구현합니다.

```
agent/
   agent_runtime.py
```

구조

```
AgentRuntime
 ├ plan()
 ├ call_llm()
 ├ call_tool()
 └ update_memory()
```

흐름

```
User
 ↓
Agent
 ↓
LLM
 ↓
Tool
 ↓
LLM
 ↓
Response
```

---

## 9. streaming support

OpenAI streaming 형태

```
text/event-stream
```

예

```
data: {"choices":[{"delta":{"content":"Hel"}}]}

data: {"choices":[{"delta":{"content":"lo"}}]}
```

구현

```
async generator
```

---

# 🔟 Multi-user concurrency

FastAPI + asyncio 사용

```
uvicorn api-server:app
```

request 흐름

```
HTTP Request
      │
async handler
      │
scheduler queue
      │
GPU batch
```

---

# 11️⃣ 추천 파일 구조

```
nano-agent-server
│
├ api-server.py
│
├ engine
│  └ nanovllm_engine.py
│
├ scheduler
│  └ request_queue.py
│
├ agent
│  └ agent_runtime.py
│
├ session
│  └ session_store.py
│
├ api
│  ├ chat.py
│  ├ completion.py
│  └ models.py
│
└ config
   └ settings.py
```

---

# 12️⃣ api-server.py 구조

핵심 흐름

```
FastAPI
  │
router
  │
agent runtime
  │
scheduler
  │
nanovllm engine
```

---

# 13️⃣ request flow

```
User
 │
POST /v1/chat/completions
 │
Router
 │
Session manager
 │
Agent runtime
 │
Scheduler queue
 │
nano-vLLM generate
 │
Streaming response
```

---

# 15️⃣ 확장 가능 기능

캡스톤 프로젝트에 매우 좋습니다.

추가 가능

### tool calling

```
function_call
```

### RAG

```
vector db
```

### agent graph

```
planner
executor
```

### monitoring

```
token/sec
latency
GPU memory
```

---

# ⭐ 핵심 포인트

이 프로젝트는 단순 API 서버가 아니라

```
LLM OS
```

구조입니다.

```
API
Session
Agent
Scheduler
Engine
```

---

# 👍 개인적으로 강력 추천

캡스톤에서 다음을 만들면 매우 좋은 프로젝트가 됩니다.

**nano-vLLM 기반 Multi-User Agent Platform**

기능

* OpenAI API
* multi-user chat
* agent tools
* streaming
* batching scheduler

---

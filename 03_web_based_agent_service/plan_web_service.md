# 🌐 웹 기반 에이전트 서비스 개발 계획 (Plan)

`02_coaching_agent`에서 개발한 Terminal UI 기반의 에이전트 로직을 웹 인터페이스로 확장하여 실제 사용 가능한 애플리케이션 서비스를 구축합니다.

---

## 1. 프로젝트 목표
- 에이전트 추론 로직과 웹 인터페이스의 분리 및 통합.
- 다중 사용자 대응이 가능한 웹 서버 구축 (선택 사항).
- 시각적으로 뛰어난 UI 제공 (Gradio) 또는 유연한 API 엔드포인트 제공 (FastAPI).

---

## 2. Web Stack 선택 가이드

### Option A: FastAPI (백엔드 중심)
- **장점**: 커스텀 프론트엔드(React, Vue 등)와 연동 가능, 상용 수준의 성능, 비동기 처리.
- **추천**: API 서버 개발에 관심이 있고, 나중에 모바일 앱이나 독립된 웹 앱을 만들고 싶은 팀.

### Option B: Gradio (UI 중심)
- **장점**: 파이썬만으로 빠르게 채팅 UI 구현 가능, 결과물을 즉시 공유하기 편리함.
- **추천**: 복잡한 웹 개발보다는 AI 모델의 기능과 UX를 빠르게 검증하고 싶은 팀.

---

## 3. 핵심 개발 과제
1. **에이전트 로직 모듈화**: TUI 코드에서 LLM 통신 로직을 별도 클래스나 함수로 분리.
2. **Endpoint 정의**: 채팅 메시지 송수신을 위한 API 설계.
3. **상태 관리**: 웹 브라우저 세션별로 대화 이력을 분리하여 관리.
4. **배포 환경 설정**: 로컬 네트워크 내에서 다른 기기가 접속 가능하도록 설정.

---

## 4. 💻 Pseudo Code: FastAPI Chat Server

```python
from fastapi import FastAPI
from pydantic import BaseModel
import anthropic

app = FastAPI()
client = anthropic.Anthropic(base_url='http://localhost:11434', api_key='ollama')

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    # 에이전트 로직 실행
    messages = req.history + [{"role": "user", "content": req.message}]
    
    response = client.messages.create(
        model='qwen2.5:7b',
        messages=messages,
        max_tokens=512
    )
    
    ai_msg = response.content[0].text
    return {"reply": ai_msg, "history": messages + [{"role": "assistant", "content": ai_msg}]}
```

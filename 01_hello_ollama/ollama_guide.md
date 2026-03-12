# 🦙 Ollama API 가이드 및 호환성 정리

Ollama는 로컬 환경에서 대규모 언어 모델(LLM)을 쉽게 사용할 수 있도록 강력한 REST API를 제공합니다. 또한 기존 AI 생태계와의 통합을 위해 OpenAI API 호환 레이어를 기본적으로 내장하고 있습니다.

---

## 1. 🛠️ Ollama 기본(Native) API
Ollama의 자체 API는 `http://localhost:11434/api` 경로를 사용합니다.

| 엔드포인트 | 설명 | 주요 용도 |
| :--- | :--- | :--- |
| `/api/generate` | 텍스트 완성(Completion) | 단발성 질문에 대한 응답 생성 |
| `/api/chat` | 대화형 응답(Chat) | 대화 맥락을 유지하는 챗봇 구현 |
| `/api/embeddings` | 텍스트 임베딩 생성 | RAG 시스템 구축을 위한 벡터 변환 |
| `/api/tags` | 로컬 모델 목록 확인 | 현재 다운로드된 모델 리스트 조회 |
| `/api/pull` | 모델 다운로드 | 새로운 모델 서버에 설치 |
| `/api/show` | 모델 정보 확인 | 모델의 파라미터, 라이선스 등 상세 정보 |

---

## 2. 🤖 OpenAI API 호환성 (OpenAI Compatibility)
Ollama는 OpenAI의 SDK나 도구를 그대로 사용할 수 있도록 **OpenAI 호환 엔드포인트**를 제공합니다. 이를 통해 기존 OpenAI 기반 코드를 최소한의 변경으로 로컬 Ollama로 전환할 수 있습니다.

### 📍 호환 엔드포인트
- `http://localhost:11434/v1/chat/completions`
- `http://localhost:11434/v1/embeddings`

### 💻 Python 코드 예시 (OpenAI SDK 사용)
```python
from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama', # 실제 키는 필요 없으나 형식상 입력
)

response = client.chat.completions.create(
  model='qwen2.5:7b',
  messages=[{"role": "user", "content": "안녕, 넌 누구니?"}]
)
print(response.choices[0].message.content)
```

---

## 3. 🦅 클로드(Claude/Anthropic) API 지원 (v0.14.0 이상)
Ollama(v0.14.0 이상)는 이제 **Anthropic Messages API와 호환**됩니다. 이를 통해 `Claude Code`와 같은 Anthropic 전용 도구를 로컬 오픈 소스 모델과 연결해 사용할 수 있습니다.

### 📍 호환 엔드포인트
- `http://localhost:11434` (Anthropic SDK의 `base_url`로 사용)

### 💻 Python 코드 예시 (Anthropic SDK 사용)
```python
import anthropic

# 1. 클라이언트 설정
client = anthropic.Anthropic(
    base_url='http://localhost:11434',
    api_key='ollama' # 형식상 입력
)

# 2. 메시지 생성
message = client.messages.create(
    model='qwen2.5:7b',
    max_tokens=1024,
    messages=[{'role': 'user', 'content': '안녕, Anthropic SDK로 인사해!'}]
)

# 3. 결과 출력
print(message.content[0].text)
```

---

## 4. 💡 요약 및 팁

1. **표준화**: 가능하면 **OpenAI 호환 엔드포인트(`/v1`)**를 사용하는 것이 범용성이 가장 높습니다.
2. **특수 도구**: `Claude Code` 등 Anthropic 전용 생태계 도구를 사용해야 할 때는 **Anthropic 호환 기능**을 활용하세요.
3. **로컬 전용**: 모델 관리나 Ollama만의 특수 기능이 필요할 때만 Native API(`/api`)를 사용하세요.

## 5. 설치
wget -qO- https://ollama.com/install.sh | sh

---
*작성일: 2026년 2월 26일*

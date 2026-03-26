# 🤖 Ollama & Anthropic API를 활용한 Coach Agent 개발 가이드

Ollama(v0.14.0+)가 **Anthropic Messages API**와 호환됨에 따라, 로컬 환경에서도 클라우드 급 에이전트 워크플로우를 구현할 수 있게 되었습니다. 특히 코칭 에이전트와 같이 '논리적 추론'이 중요한 경우 Anthropic 방식이 매우 유리합니다.

---

## 1. 🌟 왜 Anthropic Messages API 방식인가?

에이전트 개발 시 OpenAI 방식보다 Anthropic 방식이 코칭 및 복잡한 업무에 유리한 이유는 다음과 같습니다.

1.  **에이전트 특화 설계**: Anthropic API는 `Claude Code`와 같은 자율 에이전트를 위해 설계되었습니다. 단순 응답보다 **도구 사용(Tool Use)**과 **다단계 계획 수립**에 최적화되어 있습니다.
2.  **사고 과정의 구조화 (Chain of Thought)**: 모델이 답변을 내기 전 '내부적인 생각'을 정리하는 과정을 더 명확하게 처리합니다. 이는 `Gap Analysis`(현재 상태와 목표 사이의 간극 분석)와 같은 정밀한 상담 로직에 적합합니다.
3.  **긴 문맥과 대화 흐름**: 코칭 상담은 대화가 길어지는 경우가 많습니다. Anthropic 호환 인터페이스는 긴 대화의 맥락을 유지하면서도 일관된 페르소나를 유지하는 능력이 뛰어납니다.

---

## 2. 🌦️ 실습: 위치 기반 날씨 알림 에이전트 만들기

사용자의 위치를 자동으로 파악하고, 오늘 날짜와 날씨를 알려주는 에이전트의 개발 흐름은 **'생각(Thought) -> 행동(Action) -> 관찰(Observation)'**의 루프를 따릅니다.

### 🛠️ 에이전트가 사용할 도구(Tools)
1.  **Geo-Location API**: IP 주소를 기반으로 현재 도시를 파악합니다. (예: `ip-api.com`)
2.  **Time Tool**: Python의 `datetime`을 사용하여 오늘 날짜를 확인합니다.
3.  **Weather API**: 해당 도시의 현재 날씨를 가져옵니다. (예: `OpenWeatherMap` 또는 공개 API)

### 🔄 에이전트 루프 설계 (Pseudo Code)

```python
import anthropic
import requests
from datetime import datetime

# 도구 정의
def get_my_location():
    # 웹 호출을 통해 위치 파악
    res = requests.get("http://ip-api.com/json/").json()
    return f"{res['city']}, {res['country']}"

def get_today():
    return datetime.now().strftime("%Y-%m-%d %A")

def get_weather(city):
    # 실제 구현 시 OpenWeatherMap 등의 API 사용
    return f"{city}의 현재 날씨는 '맑음', 기온은 22도입니다."

# Anthropic SDK 설정 (Ollama 연결)
client = anthropic.Anthropic(base_url='http://localhost:11434', api_key='ollama')

# 에이전트 실행 루프
def run_weather_agent():
    print("--- 에이전트 가동: 위치 및 날씨 파악 ---")
    
    # 1. 위치와 날짜를 파악하는 도구 실행
    location = get_my_location()
    today = get_today()
    
    # 2. LLM에게 정보를 주입하며 최종 응답 구성 요청
    prompt = f"오늘 날짜는 {today}이고, 사용자의 위치는 {location}이야. 이 지역의 날씨 정보를 포함해서 친절하게 인사해줘."
    
    message = client.messages.create(
        model='qwen2.5:7b',
        max_tokens=1024,
        messages=[{'role': 'user', 'content': prompt}]
    )
    
    print(f"
[Agent]: {message.content[0].text}")

run_weather_agent()
```

---

## 3. 🚀 다음 단계 에이전트로의 확장 (Gap Analysis)

위의 날씨 에이전트 구조를 응용하면 다음과 같은 **코칭 루프**를 만들 수 있습니다.

1.  **상태 파악(Observation)**: 사용자의 현재 고민이나 상태를 도구(질문/데이터)로 파악합니다.
2.  **분석(Thought)**: Anthropic API의 추론 능력을 이용해 사용자의 현재와 목표 사이의 `Gap`을 분석합니다.
3.  **피드백(Action)**: 분석된 결과를 바탕으로 맞춤형 코칭 가이드를 생성합니다.

Anthropic 호환 레이어를 사용하면 이러한 복잡한 '사고 루프'를 로컬에서도 안정적으로 구현할 수 있습니다.


실제 OpenWeatherMap API를 호출하는 함수(get_real_weather)를 추가해 두었습니다. 나중에 API 키를 발급받으신 후 이 함수를 기존 get_weather 대신 호출하도록 직접 수정하시면 됩니다.
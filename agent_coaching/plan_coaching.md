# 🎯 Coach Agent 개발 프로젝트 계획 (Plan)

본 프로젝트는 Ollama와 Anthropic Messages API를 활용하여 사용자의 목표 달성을 돕는 **Terminal UI 기반 지능형 코칭 에이전트**를 구축하는 것을 목표로 합니다.

---

## 1. 프로젝트 개요 (Overview)
- **목적**: 사용자의 현재 상태(As-Is)와 목표 상태(To-Be) 사이의 간극(Gap)을 분석하고 전략을 제시하는 단기 코칭 서비스.
- **인터페이스**: **Terminal UI (TUI)** - 터미널에서의 실시간 대화.
- **핵심 기술**: Ollama, Anthropic SDK, In-Memory Session 관리.

---

## 2. 주요 단계별 개발 로드맵 (Roadmap)

### Phase 1: 기반 인프라 구축
- [x] Ollama 및 Anthropic SDK 연동 테스트.
- [ ] 코치 에이전트의 페르소나 및 시스템 프롬프트 설계.
- [ ] 파이썬 리스트를 활용한 대화 이력(Memory) 관리 구현.

### Phase 2: 코칭 로직 (Terminal UI)
- [ ] 시스템 프롬프트 내에 코칭 프레임워크(GROW 모델 등) 로직 내장.
- [ ] **Gap Analysis**: 질문 중심의 상담을 유도하는 인터랙티브 루프 개발.
- [ ] 터미널 상에서 보기 좋은 텍스트 UI/로그 출력 구성.

### Phase 3: 도구 연동 (Optional)
- [ ] 필요 시 날짜/위치 정보를 가져오는 도구 연동.

---

## 3. 💻 실습 코드: TUI Coaching Agent

```python
import anthropic

# 1. 초기화
client = anthropic.Anthropic(base_url='http://localhost:11434', api_key='ollama')
memory = [] 
system_prompt = "당신은 전문 코치입니다. 사용자의 목표를 듣고 GAP을 분석하여 질문하세요."

def run_coaching_session():
    print("="*50)
    print("🚀 [TUI] 전문 코칭 세션을 시작합니다 (종료: 'exit')")
    print("="*50)
    
    while True:
        user_input = input("
💬 [나]: ")
        if user_input.lower() in ['exit', 'quit', '종료']: 
            print("
👋 코칭을 종료합니다. 수고하셨습니다!")
            break
        
        memory.append({"role": "user", "content": user_input})
        
        response = client.messages.create(
            model='qwen2.5:7b',
            system=system_prompt,
            messages=memory,
            max_tokens=1024
        )
        
        ai_msg = response.content[0].text
        print(f"
🧠 [코치]: {ai_msg}")
        
        memory.append({"role": "assistant", "content": ai_msg})

if __name__ == "__main__":
    run_coaching_session()
```

---

## 4. 🔗 다음 단계 연동
이 단계에서 완성된 TUI 로직은 **`03_web_based_agent_service`** 프로젝트의 핵심 엔진으로 재사용됩니다. 웹 서비스 개발 단계에서는 이 로직을 FastAPI나 Gradio의 백엔드로 통합하게 됩니다.

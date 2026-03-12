# 🎯 Coach Agent 개발 프로젝트 계획 (Plan)

본 프로젝트는 Ollama와 Anthropic Messages API를 활용하여 사용자의 목표 달성을 돕고 행동 변화를 이끌어내는 **지능형 코칭 에이전트**를 구축하는 것을 목표로 합니다.

---

## 1. 프로젝트 개요 (Overview)
- **목적**: 사용자의 현재 상태(As-Is)와 목표 상태(To-Be) 사이의 간극(Gap)을 분석하고 전략을 제시하는 1회성/단기 코칭 서비스.
- **핵심 기술 스택**:
  - **LLM 엔진**: Ollama (v0.14.0 이상)
  - **추론 모델**: `qwen2.5:7b` (논리 및 한국어 성능 우수)
  - **인터페이스**: Anthropic Messages API (에이전트 워크플로우 최적화)
  - **데이터베이스**: **In-Memory Session** (실행 중 메모리에만 대화 이력 유지)

---

## 2. 주요 단계별 개발 로드맵 (Roadmap)

### Phase 1: 기반 인프라 구축 (Foundational Setup)
- [x] Ollama 및 Anthropic SDK 연동 테스트.
- [ ] 코치 에이전트의 페르소나 및 시스템 프롬프트(상담 가이드라인) 설계.
- [ ] 파이썬 리스트를 활용한 단순 대화 이력(Memory) 관리 구현.

### Phase 2: 코칭 로직 고도화 (Prompt Engineering)
- [ ] 시스템 프롬프트 내에 코칭 프레임워크(GROW 모델 등) 로직 내장.
- [ ] **1회성 세션 관리**: 프로그램 종료 시 대화 내용이 초기화되는 휘발성 세션 구조 확립.
- [ ] Gap Analysis를 위한 페르소나 주입 (질문 중심의 상담 유도).

### Phase 3: 도구 연동 및 에이전트 루프 (Agentic Loop)
- [ ] 사용자 입력 -> 추론 -> 도구 호출(날짜/위치 등) -> 최종 답변 루프 완성.
- [ ] 예외 처리 및 대화 중단/재개 로직 간단 구현.

---

## 3. 💻 Pseudo Code: In-Memory Coaching Agent

```python
import anthropic

# 1. 초기화
client = anthropic.Anthropic(base_url='http://localhost:11434', api_key='ollama')
# 세션 메모리 (휘발성)
memory = [] 
system_prompt = "당신은 전문 코치입니다. 사용자의 목표를 듣고 GAP을 분석하여 질문하세요."

def run_coaching_session():
    print("--- 코칭 세션을 시작합니다 (종료하려면 'exit' 입력) ---")
    
    while True:
        user_input = input("\n[User]: ")
        if user_input.lower() == 'exit': break
        
        # 2. 사용자 메시지 메모리에 추가
        memory.append({"role": "user", "content": user_input})
        
        # 3. LLM 호출 (과거 이력 포함)
        response = client.messages.create(
            model='qwen2.5:7b',
            system=system_prompt,
            messages=memory,
            max_tokens=1024
        )
        
        ai_msg = response.content[0].text
        print(f"\n[Coach]: {ai_msg}")
        
        # 4. AI 응답 메모리에 추가 (Context 유지)
        memory.append({"role": "assistant", "content": ai_msg})

run_coaching_session()
```

---

## 4. 🛠️ 차기 단계 확장 계획 (Future Expansion)
초기 단계 안착 후, 지속적인 코칭과 대규모 데이터 활용을 위해 다음을 도입합니다.
- **Persistent DB**: 세션 정보를 파일이나 SQLite에 저장하여 대화 재개 기능 추가.
- **RAG (FAISS/Chroma)**: 방대한 코칭 방법론 도서 및 사례집을 벡터화하여 상황별 최적의 기법을 검색(Retrieval)하여 주입.
- **Multi-Agent**: 분석가 에이전트와 전략가 에이전트를 분리하여 협업 구조 구축.

---

## 5. 기대 효과
- **단순성**: 복잡한 DB 설정 없이 즉시 코칭 루프 테스트 가능.
- **보안**: 메모리에서만 데이터가 처리되므로 세션 종료 후 데이터가 남지 않음.
- **성능**: 로컬 메모리 참조로 인해 검색 지연 시간 최소화.

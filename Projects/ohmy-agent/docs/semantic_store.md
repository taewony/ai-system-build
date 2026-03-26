## 순수 파이썬(Pure Python)과 파일 I/O만으로 도메인 모델(Book, Chapter, Knowledge)을 확실하게 캡슐화

### 📂 예상 작업 폴더 구조
```text
ohmy-agent/
├── core/
│   ├── semantic_store.py  <-- [지금 작성할 코드]
│   └── agent_loop.py
├── workspace/             <-- [에이전트가 관리할 파일들이 자동 생성될 곳]
│   ├── playbook_meta.yaml
│   ├── knowledge_base.yaml
│   └── chapters/
│       ├── chapter_1.md
│       └── ...
└── spak.py
```

### 💻 `core/semantic_store.py` 구현 코드

파이썬의 기본 딕셔너리를 메모리(In-memory) 저장소로 사용하고, 변경 사항이 생길 때마다 즉시 `yaml` 파일과 `.md` 파일로 디스크에 동기화(Sync)하는 구조입니다. (실행을 위해 터미널에서 `pip install pyyaml`이 필요할 수 있습니다.)

### 설계의 핵심 포인트

1. **관심사의 분리 (Separation of Concerns):** 에이전트(`agent_loop.py`)는 디스크에 파일을 어떻게 쓸지, YAML을 어떻게 파싱할지 전혀 몰라도 됩니다. 그저 `store.add_chapter("개요", "내용...")` 이라고 호출하기만 하면 완벽하게 생성됩니다.
2. **MD와 YAML의 하이브리드 보관:** 메타데이터(제목, 상태, 파일경로)는 가벼운 `yaml`로 관리하여 에이전트가 전체 목차를 빠르게 파악할 수 있게 하고, 길고 복잡한 HTML/마크다운 본문은 별도의 `.md` 파일로 빼내어 Lit/Vite 렌더링에 방해가 되지 않도록 설계했습니다.
3. **간이 시맨틱 서치 (`recall_knowledge`):** 현재는 단순 `in` 연산자(키워드 매칭)를 썼지만, 나중에 이 함수 내부만 `index.as_query_engine().query(query)` (LlamaIndex 코드)로 바꾸면 에이전트 입장에서는 똑같은 함수를 쓰면서 성능만 마법처럼 올라가게 됩니다.

이제 이 튼튼한 `SemanticStore`를 에이전트가 마음껏 주무를 수 있게 연결할 차례입니다. 방금 만든 **이 클래스를 Streamlit 화면(`spak.py`)의 버튼 클릭만으로 직접 구동해 보면서 YAML과 MD 파일이 로컬 폴더에 예쁘게 생성되는지 눈으로 확인해 보는 테스트 코드**를 작성해 드릴까요? 아니면 곧바로 **Agent Loop에 이 Store를 Tool로 주입하는 단계**로 넘어갈까요?
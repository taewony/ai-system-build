# 📘 [프로젝트 명세서] AI Agent Programming 플레이북 자동 생성

## 1. 전체 UI 구성 (System UI Layout)

출판 편집자(User)가 시스템을 조작하고 결과를 확인하는 화면은 **듀얼 모니터 또는 스플릿 뷰(Split View)** 형태로 구성됩니다.

* **좌측 화면: SPAK Dashboard (Streamlit)**
    * **Role:** 지휘 통제실 (Command Center)
    * **구성 요소:**
        * 작업 지시서(`.md`) 업로드 패널
        * 에이전트의 실시간 상태 로그 (Thought, Action, Observation 스트리밍)
        * 에이전트가 현재 수집/활용 중인 지식(Given-When-Then) 표시창
* **우측 화면: Online Playbook (Vite + Lit)**
    * **Role:** 최종 결과물 라이브 프리뷰 (Live Preview)
    * **구성 요소:**
        * Lit 컴포넌트로 렌더링된 세련된 웹 플레이북 화면.
        * 좌측 사이드바: 에이전트가 생성한 목차(TOC) 네비게이션.
        * 메인 영역: 현재 선택된 챕터의 렌더링된 본문 (코드 블록 하이라이팅, 다이어그램 등).
        * *특징:* 에이전트가 `workspace`의 파일을 수정할 때마다 Vite의 HMR(Hot Module Replacement) 기능으로 새로고침 없이 즉시 결과가 화면에 반영됩니다.

---

## 2. 파일 및 데이터 구조 (SemanticStore 물리 구성)

에이전트가 `SemanticStore` API를 호출하여 생성한 로컬 `workspace/` 디렉토리의 실제 모습입니다.

```text
workspace/
├── playbook_meta.yaml      # 책의 전체 뼈대와 목차 (Agent가 생성 및 관리)
├── knowledge_base.yaml     # 편집 가이드라인 (Given-When-Then)
└── chapters/               # 실제 본문 내용 (Lit 컴포넌트가 파싱하여 화면에 뿌려줌)
    ├── ch_intro.md         # 서론
    ├── ch_ollama.md        # 1. Ollama (GGUF, 로컬 서빙)
    ├── ch_nanovllm.md      # 2. nano-vLLM (Safetensors, GPU 최적화)
    ├── ch_openclaw.md      # 3. openclaw (도구 호출 특화)
    ├── ch_hermes.md        # 4. Hermes agent (자율형 에이전트 루프)
    └── ch_outro.md         # 결론
```

### 📄 데이터 덤프 예시 (`playbook_meta.yaml`)
에이전트가 전체 구조를 기획(Plan)한 결과물입니다. Lit 기반의 웹 프론트엔드는 이 파일을 읽어 좌측 네비게이션 메뉴를 자동으로 그립니다.
```yaml
book_title: "AI Agent Programming"
status: "drafting"
chapters:
  - id: "ch_intro"
    title: "Introduction to Local AI Agents"
    file_link: "./chapters/ch_intro.md"
  - id: "ch_ollama"
    title: "1. Ollama: Lightweight Local Serving"
    file_link: "./chapters/ch_ollama.md"
  - id: "ch_nanovllm"
    title: "2. nano-vLLM: High-Performance GPU Inference"
    file_link: "./chapters/ch_nanovllm.md"
  - id: "ch_openclaw"
    title: "3. OpenClaw: Mastering Tool Calling"
    file_link: "./chapters/ch_openclaw.md"
  - id: "ch_hermes"
    title: "4. Hermes Agent: Autonomous ReAct Loops"
    file_link: "./chapters/ch_hermes.md"
```

---

## 3. 워크플로우 아웃라인 (Plan-and-Solve Workflow)

사용자가 "4가지 도구를 소개하는 책을 써줘"라고 요청했을 때, 에이전트가 자율적으로 작업을 수행하는 단계별 시나리오입니다.

### Step 1: 작업 지시 및 초기 기획 (Planning)
1.  **User Action:** SPAK Dashboard에 `draft_request.md` (주제: Ollama, nano-vllm, openclaw, Hermes agent를 다루는 코딩 가이드북 작성)를 업로드.
2.  **Agent Action (Plan):** * 요구사항을 분석하여 6개의 하위 태스크(서론, 4개 도구, 결론)로 작업 분해(Sub-tasks).
    * `SemanticStore.set_book_title("AI Agent Programming")` 호출.
    * 목차 뼈대를 구상하여 `playbook_meta.yaml` 생성.

### Step 2: 지식 검색 및 콘텐츠 집필 (Solving & Tool Calling)
에이전트는 기획된 태스크 리스트를 순회하며 챕터별로 아래 작업을 반복합니다.

1.  **지식 확인:** `SemanticStore.recall_knowledge("CLI tool format")` 호출.
    * *(결과 수신)* "Given CLI 도구 설명 시, When 설치 명령어를 적을 때, Then 반드시 `bash` 코드 블록을 사용한다."
2.  **정보 검색 (Web Search):** "OpenClaw latest features" 등을 검색하여 최신 API 스펙 확보.
3.  **본문 작성 (Heavy LLM Offloading):**
    * 내용이 길고 복잡한 코드 예제 생성이 필요하므로 로컬 vLLM 대신 Tool을 통해 Gemini API 호출.
    * "Hermes Agent의 Python 에이전트 루프 예제 코드를 포함한 마크다운 챕터를 작성해 줘."
4.  **저장:** 결과물을 받아 `SemanticStore.add_chapter("4. Hermes Agent", <생성된_마크다운_텍스트>)` 호출.

### Step 3: 실시간 렌더링 및 검토 (Review)
1.  **System Action:** `workspace/`에 파일이 추가될 때마다 Vite 서버가 이를 감지하여 우측 Playbook 화면을 갱신.
2.  **User Action:** 사용자는 실시간으로 완성되어 가는 플레이북을 읽어봄. "nano-vLLM 챕터에 vLLM과의 속도 비교 표(Table)가 빠졌네."라고 판단.

### Step 4: 타겟 수정 (Targeted Revision)
1.  **User Action:** Dashboard에 `revision.md` 업로드. ("2장 nano-vLLM 부분에 vLLM 대비 메모리 점유율 비교 표를 추가해.")
2.  **Agent Action:**
    * 전체를 다시 쓰는 것이 아니라, `playbook_meta.yaml`을 읽고 "2장"의 ID가 `ch_nanovllm`임을 파악.
    * 해당 파일만 읽어온 뒤, 비교 표를 추가하여 재생성.
    * `SemanticStore.update_chapter_content("ch_nanovllm", <수정된_마크다운>)` 호출.
3.  **System Action:** Vite 서버가 해당 페이지의 표(Table) 부분만 즉시 리렌더링.

---

성공적으로 파일이 생성된 것을 축하합니다! 캡처 화면을 보니 에이전트가 `SemanticStore`를 완벽하게 조작했네요.

### 🔍 파일 이름이 왜 저렇게 이상할까요?
파일 이름이 `ch_3c6724fe.md`처럼 복잡한 해시(UUID) 값으로 되어 있는 것은 **에이전트가 파일명 충돌을 방지하기 위한 엔터프라이즈급 설계**입니다. 

만약 제목 그대로 `1. Ollama.md`라고 저장했다가 나중에 제목이 바뀌거나, 띄어쓰기나 특수문자가 들어가면 경로 에러가 발생하기 쉽습니다. 그래서 **사람은 `playbook_meta.yaml`을 통해 깔끔한 목차(제목)를 보고, 시스템(Agent와 Lit)은 고유 ID로 파일을 추적**하도록 분리한 것입니다. (앞서 `semantic_store.py` 코드에서 `uuid.uuid4().hex[:8]`로 생성하도록 설계해 두었습니다.)

---

### 🚀 Vite + Lit으로 Online Playbook 실행하기

이제 생성된 파일들을 브라우저에서 예쁘게 보여줄 차례입니다. 앞서 요구사항에 명시하신 대로 **Lit 컴포넌트와 Vite**를 사용하여 마크다운을 HTML로 렌더링하는 뷰어(Viewer)를 만들어 보겠습니다.

터미널을 열고 `ohmy-agent` 폴더 바깥(상위 폴더)에서 다음 단계들을 순서대로 실행해 주세요.

#### 1단계: Vite + Lit 프로젝트 생성 및 패키지 설치
```bash
# 1. playbook-web 이라는 이름으로 Vite+Lit 템플릿 생성
npm create vite@latest playbook-web -- --template lit

# 2. 폴더로 이동 및 기본 패키지 설치
cd playbook-web
npm install

# 3. YAML과 Markdown을 브라우저에서 읽기 위한 파서 라이브러리 설치
npm install js-yaml marked
```

#### 2단계: 에이전트의 Workspace를 Vite로 연결
Vite 웹 서버가 에이전트가 만든 파일들을 정적 리소스(Static Asset)로 읽을 수 있어야 합니다. 가장 간단한 방법은 **방금 만들어진 `workspace` 폴더를 통째로 복사해서 `playbook-web/public/` 폴더 안으로 붙여넣는 것**입니다.

* **결과 경로:** `playbook-web/public/workspace/playbook_meta.yaml`

#### 3단계: Lit 컴포넌트 작성 (`src/my-element.js` 덮어쓰기)
Vite가 만들어준 기본 `src/my-element.js` 파일의 내용을 전부 지우고, 아래 코드로 교체합니다. 이 코드는 `playbook_meta.yaml`을 읽어 사이드바를 만들고, 클릭하면 마크다운을 HTML로 변환해 보여줍니다.

```javascript
import { LitElement, html, css } from 'lit';
import { marked } from 'marked';
import yaml from 'js-yaml';

export class PlaybookApp extends LitElement {
  static properties = {
    meta: { type: Object },
    currentContent: { type: String }
  };

  static styles = css`
    :host {
      display: flex;
      font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
      height: 100vh;
      color: #333;
    }
    .sidebar {
      width: 300px;
      background-color: #f4f4f9;
      padding: 20px;
      border-right: 1px solid #ddd;
      overflow-y: auto;
    }
    .sidebar h2 { font-size: 1.2rem; margin-bottom: 20px; }
    .sidebar ul { list-style: none; padding: 0; }
    .sidebar li { margin-bottom: 10px; }
    .sidebar a {
      text-decoration: none;
      color: #0066cc;
      font-weight: bold;
      cursor: pointer;
    }
    .sidebar a:hover { text-decoration: underline; }
    .content {
      flex: 1;
      padding: 40px;
      overflow-y: auto;
      line-height: 1.6;
    }
    .content pre {
      background-color: #282c34;
      color: #abb2bf;
      padding: 15px;
      border-radius: 5px;
      overflow-x: auto;
    }
  `;

  constructor() {
    super();
    this.meta = null;
    this.currentContent = "<h1>Welcome</h1><p>왼쪽 목차에서 챕터를 선택하세요.</p>";
    this.loadMeta();
  }

  // 1. YAML 파일 읽어오기
  async loadMeta() {
    const response = await fetch('/workspace/playbook_meta.yaml');
    const text = await response.text();
    this.meta = yaml.load(text);
  }

  // 2. 마크다운 파일 읽어서 HTML로 변환하기
  async loadChapter(fileLink) {
    // YAML의 "./chapters/..." 경로를 "/workspace/chapters/..."로 변환
    const url = `/workspace${fileLink.substring(1)}`;
    const response = await fetch(url);
    const mdText = await response.text();
    this.currentContent = marked.parse(mdText);
  }

  render() {
    if (!this.meta) return html`<div>Loading Playbook...</div>`;

    return html`
      <div class="sidebar">
        <h2>${this.meta.book_title}</h2>
        <ul>
          ${this.meta.chapters.map(ch => html`
            <li>
              <a @click=${(e) => { e.preventDefault(); this.loadChapter(ch.file_link); }}>
                ${ch.title}
              </a>
            </li>
          `)}
        </ul>
      </div>
      <div class="content" .innerHTML=${this.currentContent}></div>
    `;
  }
}

customElements.define('playbook-app', PlaybookApp);
```

#### 4단계: `index.html` 수정 및 실행
`playbook-web` 폴더의 루트에 있는 `index.html`을 열어서 `<my-element>` 태그를 `<playbook-app>`으로 변경합니다.

```html
<body>
  <playbook-app></playbook-app> <script type="module" src="/src/my-element.js"></script>
</body>
```

이제 터미널에서 실행해 보세요!
```bash
npm run dev
```

터미널에 표시된 `http://localhost:5173` 링크를 클릭하면, 방금 전 에이전트가 작성한 "AI Agent Programming" 책이 세련된 웹 UI로 나타나고, 목차를 클릭할 때마다 내용이 예쁘게 렌더링될 것입니다. 

결과가 잘 나오는지 확인해 보시고, 에이전트(`agent_loop.py`)의 작업 경로를 아예 `playbook-web/public/workspace`로 고정해서 실시간 연동을 구성해 볼까요?
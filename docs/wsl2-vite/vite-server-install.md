# WSL2 기반 Lit + Vite 개발환경 구축

## 0. 목적

1. WSL2 환경에서 최신 Node.js 설치 (nvm 기반)
2. Lit + Vite 프로젝트 생성 및 서버 실행
3. Windows 측에서 curl로 HTTP 응답 확인

---

## 1. 사전 상태 확인

WSL2가 이미 설치되어 있다고 가정한다.

### 1.1 WSL 접속

```bash
wsl
```

---

### 1.2 기존 Node 제거 여부 확인

```bash
node -v
which node
```

#### 문제 상황

* `/usr/bin/node` → apt로 설치된 구버전
* Node 18 이하 → 최신 tooling과 충돌 가능

---

## 2. nvm 기반 Node 최신 설치

## 2.1 nvm 설치

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

```bash
source ~/.bashrc
```

---

## 2.2 Node 최신 버전 설치

```bash
nvm install 22
nvm use 22
```

---

## 2.3 기본 버전 설정

```bash
nvm alias default 22
```

---

## 2.4 설치 확인

```bash
node -v
npm -v
```

예상 결과:

```bash
v22.x.x
10.x.x 이상
```

---

## 3. Lit + Vite 프로젝트 생성

## 3.1 프로젝트 생성

```bash
npm create vite@latest
```

입력 예:

```text
✔ Project name: lit-app
✔ Select a framework: lit
✔ Select a variant: JavaScript
```

---

## 3.2 프로젝트 이동 및 설치

```bash
cd lit-app
npm install
```

---

## 3.3 Lit 라이브러리 설치

```bash
npm install lit
```

---

## 3.4 Lit 컴포넌트 작성

`src/main.js` 수정:

```javascript
import { LitElement, html, css } from 'lit';

class MyApp extends LitElement {
  static styles = css`
    h1 {
      color: blue;
    }
  `;

  render() {
    return html`<h1>Hello from Lit + WSL2</h1>`;
  }
}

customElements.define('my-app', MyApp);

document.body.appendChild(document.createElement('my-app'));
```

---

## 4. Vite 서버 실행

## 4.1 기본 실행

```bash
npm run dev
```

출력 예:

```text
Local: http://localhost:5173
```

---

## 4.2 외부 접근 허용 (중요)

WSL → Windows 접근을 확실히 하기 위해:

```bash
npm run dev -- --host
```

또는 `vite.config.js`:

```javascript
export default {
  server: {
    host: true
  }
}
```

---

## 5. Windows에서 접속 확인

## 5.1 브라우저 확인

Windows에서:

```text
http://localhost:5173
```

---

## 5.2 curl로 HTTP 요청 검증

### Windows PowerShell:

```powershell
curl http://localhost:5173
```

---

## 5.3 예상 결과

* HTML 문서 반환
* `<script type="module">` 포함된 Vite 기본 템플릿

---

## 6. 네트워크 동작 원리 (핵심 이해)

### 구조

```
[WSL2 Linux]
  └─ Vite Dev Server (5173)

        ↓ shared localhost

[Windows Host]
  └─ Browser / curl
```

---

### 핵심 포인트

* WSL2는 Windows와 **localhost 네트워크 공유**
* 별도 포트포워딩 불필요
* `--host` 옵션으로 외부 접근 안정화

---

## 7. 문제 해결 가이드

### 7.1 접속 안 되는 경우

#### 원인 1: host 바인딩 제한

해결:

```bash
npm run dev -- --host
```

---

#### 원인 2: 포트 확인

```bash
lsof -i :5173
```

---

#### 원인 3: 방화벽

* Windows Defender → 허용 필요

---

### 7.2 Node 버전 문제

```bash
node -v
```

* 20 이상 필요
* 낮으면 nvm으로 교체

---

## 8. 검증 체크리스트

| 항목           | 확인 |
| ------------ | -- |
| Node 최신 버전   | ✔  |
| Vite 서버 실행   | ✔  |
| localhost 접속 | ✔  |
| curl 응답 확인   | ✔  |

---

## 9. 확장 방향 (다음 단계)

* FastAPI / Express API 서버 추가
* Lit + SSR 구조 설계
* WSL2 + Docker + GPU 연동
* Reverse proxy (Nginx) 구성

---

## 10. 요약

* nvm으로 Node 최신 설치가 핵심
* Vite + Lit은 즉시 실행 가능
* WSL2와 Windows는 localhost 공유
* curl로 네트워크 레벨 검증 가능

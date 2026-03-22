import os
import re
import asyncio
from openai import AsyncOpenAI

# -----------------------------------
# 1. Config (설정)
# -----------------------------------
# 로컬 Ollama 서버 또는 호환 API 설정
MODEL = "qwen3.5:9b"
BASE_URL = "http://localhost:11434/v1"

# 최대 자동 복구 시도 횟수
MAX_REPAIR_ITER = 3

client = AsyncOpenAI(
    base_url=BASE_URL,
    api_key="ollama" # Ollama는 아무 키나 입력해도 동작합니다
)

# -----------------------------------
# 2. Prompts (프롬프트 설계)
# -----------------------------------
GEN_SYSTEM_PROMPT = """
You are a senior frontend engineer.

Generate a COMPLETE, self-contained index.html file that visualizes the Quick Sort algorithm.

STRICT REQUIREMENTS:
- Single HTML file
- No external dependencies
- Use vanilla JS
- Use requestAnimationFrame (MANDATORY)
- Use async/await for animation steps
- No blocking loops (NO while(true), NO heavy sync recursion)
- Include:
  - array bars visualization
  - pivot highlight
  - swap animation
  - start/reset buttons

Output ONLY HTML code. Do not include markdown formatting if possible.
"""

FIX_SYSTEM_PROMPT = """
You are a senior frontend debugging expert.

Task:
- Analyze the given HTML/JS
- Fix animation freeze / infinite loop / async issues

Common issues to fix:
- blocking loops
- missing await
- recursion without yielding
- event loop starvation

MANDATORY:
- Use requestAnimationFrame
- Ensure animation progresses step-by-step

Output ONLY fixed full HTML. Do not include markdown formatting if possible.
"""

# -----------------------------------
# 3. Streaming (스트리밍 출력)
# -----------------------------------
async def stream_llm(messages):
    """LLM의 응답을 스트리밍으로 받아오며 콘솔에 출력합니다."""
    stream = await client.chat.completions.create(
        model=MODEL,
        messages=messages,
        stream=True,
        temperature=0.4,
        max_tokens=8192,
    )

    full_text = ""

    async for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        print(delta, end="", flush=True)
        full_text += delta

    print("\n\n[✔] Stream complete\n")
    return full_text


# -----------------------------------
# 4. Utils (유틸리티)
# -----------------------------------
def strip_code_block(text: str) -> str:
    """마크다운 코드 블록(```html ... ```)을 추출합니다."""
    # ```html 또는 ```으로 시작하는 코드 블록 매칭
    match = re.search(r"```(?:html)?\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return text.strip()


def save_file(path: str, content: str) -> None:
    """파일을 저장합니다."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"[✔] Saved: {path}")
    except Exception as e:
        print(f"[ERROR] Failed to save {path}: {e}")


# -----------------------------------
# 5. Validation (정적 검증 필터)
# -----------------------------------
def validate_html(code: str):
    """생성된 HTML/JS 코드의 핵심 로직(비동기, 애니메이션)을 정적으로 검사합니다."""
    issues = []

    if "requestAnimationFrame" not in code:
        issues.append("Missing requestAnimationFrame (Required for UI rendering)")

    if re.search(r"while\s*\(\s*true\s*\)", code):
        issues.append("Infinite loop detected (Will block the main thread)")

    if "async function" not in code and "async " not in code:
        issues.append("No async function used (Needed for step-by-step animation)")

    if "await" not in code:
        issues.append("Missing await (Animation will likely complete instantly, blocking UI)")

    # 간단한 재귀 호출 시 await 누락 체크 (완벽하진 않으나 훌륭한 휴리스틱)
    if "quickSort(" in code and "await quickSort" not in code:
        issues.append("Recursive call without await (Will cause instant sorting)")

    return issues


# -----------------------------------
# 6. Generation (최초 생성)
# -----------------------------------
async def generate_html():
    """초기 HTML을 생성합니다."""
    print("[INFO] Generating HTML...\n")

    raw = await stream_llm([
        {"role": "system", "content": GEN_SYSTEM_PROMPT},
        {"role": "user", "content": "visualize quick sort algorithm into self-contained index.html"}
    ])

    return strip_code_block(raw)


# -----------------------------------
# 7. Auto Repair (자동 수정 로직)
# -----------------------------------
async def fix_html(code, issues):
    """발견된 이슈를 기반으로 코드를 수정합니다."""
    print(f"\n[INFO] Fixing issues: {issues}\n")

    raw = await stream_llm([
        {"role": "system", "content": FIX_SYSTEM_PROMPT},
        {
            "role": "user",
            "content": f"""
The following HTML has issues:

Issues:
{issues}

Fix the code:

```html
{code}
```
"""
        }
    ])
    return strip_code_block(raw)


async def repair_loop(initial_code):
    """검증과 수정을 반복하는 Self-healing 루프입니다."""
    code = initial_code
    
    for i in range(MAX_REPAIR_ITER):
        print(f"\n[DEBUG] Validation pass {i+1}/{MAX_REPAIR_ITER}")

        issues = validate_html(code)

        if not issues:
            print("[✔] Validation passed! No issues found.")
            return code

        print(f"[WARN] Issues found: {issues}")
        
        # 이슈가 있다면 fix_html 호출
        code = await fix_html(code, issues)

    print("\n[WARN] Max repair iterations reached. Returning the latest code.")
    return code


# -----------------------------------
# 8. Main Pipeline (메인 오케스트레이션)
# -----------------------------------
async def main():
    target_file = "index.html"
    
    if not os.path.exists(target_file):
        print("[INFO] Starting generation pipeline...\n")
        # Step 1: 생성
        code = await generate_html()
        
        # Step 2: 검증 + 자동 수정 루프
        code = await repair_loop(code)

        # Step 3: 최종 파일 저장
        save_file(target_file, code)

    else:
        print(f"[INFO] Existing {target_file} detected → Starting repair pipeline...\n")

        with open(target_file, "r", encoding="utf-8") as f:
            existing_code = f.read()

        # 기존 코드를 바로 수리 루프에 투입
        fixed_code = await repair_loop(existing_code)

        # 새 파일명으로 저장하여 버전 관리 효과
        save_file("index_01.html", fixed_code)


# -----------------------------------
# 9. Execution (실행 진입점)
# -----------------------------------
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n[INFO] Pipeline stopped by user.")
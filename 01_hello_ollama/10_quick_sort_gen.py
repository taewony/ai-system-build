from openai import OpenAI
import os

# -----------------------------
# 1. Ollama OpenAI-compatible client 설정
# -----------------------------
client = OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama endpoint
    api_key="ollama"  # dummy key (required but not validated)
)

# -----------------------------
# 2. Prompt 정의
# -----------------------------
SYSTEM_PROMPT = """
You are a senior frontend engineer.

Generate a COMPLETE, self-contained index.html file that visualizes the Quick Sort algorithm.

Requirements:
- Single HTML file (no external JS/CSS)
- Use vanilla JavaScript
- Include:
  - Visualization of array bars
  - Step-by-step animation
  - Highlight pivot, swaps, partitions
  - Start / Reset buttons
- Clean UI (CSS included inside <style>)
- Code must be runnable immediately in browser
- No explanations, only code
"""

USER_PROMPT = "visualize quick sort algorithm into self-contained index.html"


# -----------------------------
# 3. LLM 호출
# -----------------------------
response = client.chat.completions.create(
    model="qwen3.5:9b",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": USER_PROMPT}
    ],
    temperature=0.7,
    max_tokens=4096,
)

# -----------------------------
# 4. 결과 추출
# -----------------------------
html_code = response.choices[0].message.content

# (선택) ```html 코드블록 제거
def strip_code_block(text):
    if text.startswith("```"):
        lines = text.split("\n")
        return "\n".join(lines[1:-1])
    return text

html_code = strip_code_block(html_code)

# -----------------------------
# 5. 파일 저장
# -----------------------------
output_path = "index.html"
with open(output_path, "w", encoding="utf-8") as f:
    f.write(html_code)

print(f"[✔] index.html generated at: {os.path.abspath(output_path)}")
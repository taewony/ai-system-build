# 2. 스트리밍 응답 받기

import ollama

model = 'qwen2.5:7b'
stream = ollama.chat(
    model=model,
    messages=[{'role': 'user', 'content': '한국의 수도는?'}],
    stream=True,
)

for chunk in stream:
    print(chunk['message']['content'], end='', flush=True)
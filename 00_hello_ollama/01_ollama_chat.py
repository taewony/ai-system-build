# 01 기본 채팅 예제

import ollama

model = 'qwen2.5:7b'
response = ollama.chat(model=model, messages=[
    {
        'role': 'user',
        'content': '왜 하늘은 파란가요?',
    },
])
print(response['message']['content'])
# or access fields directly from the response object
# print(response.message.content)
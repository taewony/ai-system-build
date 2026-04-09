from openai import OpenAI

# Windows에서 WSL2 서버로 접속
client = OpenAI(
    base_url="http://localhost:8000/v1", 
    api_key="not-needed"
)

completion = client.chat.completions.create(
    model="qwen3-0.6b",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Windows에서 WSL2로 보낸 메시지입니다!"}
    ]
)

print(completion.choices[0].message.content)
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy"
)

resp = client.chat.completions.create(
    model="qwen3",
    messages=[
        {"role":"user","content":"introduce yourself"}
    ]
)

print(resp.choices[0].message.content)
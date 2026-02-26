# OpenAI SDK를 사용하여 Ollama와 통신하기
# 이 방식은 나중에 GPT-4나 다른 클라우드 AI로 전환할 때 코드 변경을 최소화할 수 있는 표준 방식입니다.

from openai import OpenAI

# 1. 클라이언트 설정
# base_url에 '/v1'을 붙여 OpenAI 호환 엔드포인트를 사용합니다.
# api_key는 Ollama에서 검증하지 않지만, SDK 형식을 맞추기 위해 아무 값이나 입력합니다.
client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)

model = 'qwen2.5:7b'

print(f"--- OpenAI SDK를 통해 {model} 모델에 질문을 보냅니다. ---")

# 2. 채팅 요청 생성 (OpenAI 표준 문법)
response = client.chat.completions.create(
    model=model,
    messages=[
        {
            "role": "system",
            "content": [
            {
                "type": "text",
                "text": "You are a python expert."
            }
            ]
        },
        {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text":  "Code a Python function to generate a Fibonacci sequence."
                }
            ]
        }
    ],
)

# 3. 결과 출력
# OpenAI 응답 객체의 구조(choices[0].message.content)를 따릅니다.
print("[AI 응답]:")
print(response.choices[0].message.content)

print("--- 실행 완료 ---")

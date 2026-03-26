from openai import OpenAI

client = OpenAI(
    base_url='http://localhost:11434/v1/',
    api_key='ollama',
)
model = 'qwen3:8b'

# 대화 내역을 저장할 리스트 선언 
message_history = [
    {'role': 'system', 'content': '모든 답변을 한국어로 작성하세요.'}
]
# 대화 시작
while True:
    user_input = input("사용자: ")
    # 사용자의 질문을 리스트에 추가 
    message_history.append({"role": "user", "content": user_input})
    # API 요청 및 응답
    chat_completion = client.chat.completions.create(
        messages = message_history,
        model = model,
    )
    # 챗봇의 응답을 리스트에 추가
    assistant_response = chat_completion.choices[0].message.content
    message_history.append({"role": "assistant", "content": assistant_response})
    # 응답 결과 출력
    print(f"챗봇: {assistant_response}")
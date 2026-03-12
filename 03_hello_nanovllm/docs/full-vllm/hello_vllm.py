# pip install openai
from openai import OpenAI

# 1. vLLM 서버 주소 설정 (기본 포트 8000)
# 서버가 로컬에서 실행 중이므로 localhost를 사용합니다.
client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="token-not-needed", # vLLM은 기본적으로 키가 필요 없지만 형식상 입력합니다.
)

# 2. 프롬프트 및 모델 설정
# 서버 실행 시 입력한 모델명과 동일해야 합니다.
model_name = "deepseek-ai/deepseek-coder-7b-instruct-v1.5"

# 3. 채팅 형식의 요청 (Chat Completion)
response = client.chat.completions.create(
    model=model_name,
    messages=[
        {"role": "system", "content": "You are a helpful assistant and expert in Information Processing Engineer exam."},
        {"role": "user", "content": "정보처리기사 시험에서 '정규화(Normalization)'의 목적을 3가지만 알려줘."}
    ],
    temperature=0.7,
    max_tokens=500
)

# 4. 결과 출력
print("-" * 30)
print(f"답변: \n{response.choices[0].message.content}")
print("-" * 30)
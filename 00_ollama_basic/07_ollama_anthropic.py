import anthropic

# Ollama v0.14.0 이상부터는 Anthropic SDK(Messages API)와 호환됩니다.
# 이를 통해 Claude 전용 라이브러리나 도구들을 로컬 모델과 연결하여 사용할 수 있습니다.

# 1. 클라이언트 설정
# base_url을 로컬 Ollama 서버 주소(http://localhost:11434)로 지정합니다.
# api_key는 Ollama에서 무시되지만, SDK의 필수 요구사항이므로 'ollama'를 입력합니다.
client = anthropic.Anthropic(
    base_url='http://localhost:11434',
    api_key='ollama'
)

# 사용하려는 로컬 모델명을 입력합니다.
model = 'qwen2.5:7b' 

print(f"--- [Step 1] Anthropic SDK를 통해 {model} 모델에 연결되었습니다. ---")

# 2. 메시지 생성 요청
# Anthropic 고유의 Messages API 형식을 그대로 사용합니다.
print(f"--- [Step 2] Anthropic 스타일로 질문을 전송 중입니다... ---")
try:
    message = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[
            {
                'role': 'user', 
                'content': '로컬 LLM과 Anthropic SDK를 함께 쓰면 어떤 장점이 있는지 짧게 알려줘.'
            }
        ]
    )

    # 3. 결과 출력
    # Anthropic 응답 구조(message.content[0].text)에 맞춰 텍스트를 추출합니다.
    print("" + "="*50)
    print("[Anthropic SDK 스타일 응답]:")
    print(message.content[0].text)
    print("="*50)

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    print("팁: Ollama 버전이 v0.14.0 이상인지 확인하고, 모델이 설치되어 있는지 확인하세요.")

print("--- 실행이 완료되었습니다. ---")

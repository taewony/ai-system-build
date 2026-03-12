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
model = 'qwen3:8b' 

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

    print("="*50)
    print("[Anthropic SDK 스타일 응답]:")
    
    # 수정된 부분: content 리스트를 돌며 TextBlock만 추출
    full_text = ""
    for block in message.content:
        # block이 TextBlock 타입인 경우에만 text를 가져옴
        if hasattr(block, 'text'):
            full_text += block.text
        # 만약 ThinkingBlock이라면 무시하거나 별도로 처리 가능
        elif hasattr(block, 'thinking'):
            print(f"[모델의 생각]: {block.thinking}\n")

    print(full_text)
    print("="*50)

except Exception as e:
    print(f"❌ 오류 발생: {e}")

print("--- 실행이 완료되었습니다. ---")

import ollama

# WSL2의 localhost:11434로 연결하는 클라이언트 객체 생성
# (기본값이 http://localhost:11434 이므로 생략해도 무방합니다)
client = ollama.Client(host='http://172.23.71.197:11434')

print("Qwen3:8b 모델에 질문을 전송하는 중...\n")

# 모델에 프롬프트 전송
response = client.chat(
    model='qwen3:8b',
    messages=[
        {
            'role': 'user',
            'content': 'GPU 커널 프로그래밍의 장점을 3줄로 요약해줘.'
        }
    ]
)

# 결과 출력
print("=== ollama server 답변 결과 ===")
print(response['message']['content'])

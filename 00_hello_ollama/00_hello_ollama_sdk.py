# 서버가 켜진 후 실행
import ollama

# pull한 모델명과 정확히 일치해야 합니다.
response = ollama.generate(model='qwen3:8b', prompt='안녕, 자기소개 좀 해줘.')

print(response['response'])
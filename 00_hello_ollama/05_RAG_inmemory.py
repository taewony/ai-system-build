import ollama

# 1. 문서 준비
documents = [
    "하늘이 파란 이유는 레일리 산란 때문이다.",
    "바다가 파란 이유도 하늘의 반사와 산란 때문이다.",
    "일몰 때 하늘이 붉게 보이는 이유는 빛의 경로가 길어져 파장이 긴 빛만 남기 때문이다."
]
model_embed='nomic-embed-text'
# 2. 문서 임베딩 생성 (벡터 DB에 저장할 수 있음)
doc_embeddings = [ollama.embeddings(model=model_embed, prompt=doc)['embedding'] for doc in documents]

# 3. 사용자 질문
query = "왜 하늘은 파란가요?"
query_emb = ollama.embeddings(model=model_embed, prompt=query)['embedding']

# 4. 가장 유사한 문서 찾기 (코사인 유사도 등)
import numpy as np
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

similarities = [cosine_similarity(query_emb, doc_emb) for doc_emb in doc_embeddings]
best_doc = documents[np.argmax(similarities)]
print(f"참고 자료: {best_doc}")

# 5. LLM에 프롬프트 구성 (검색된 문서 포함)
model_chat = 'qwen3:8b'
response = ollama.chat(model=model_chat, messages=[
    {'role': 'system', 'content': f"참고 자료: {best_doc}"},
    {'role': 'user', 'content': query}
])
print(response['message']['content'])
# 🚀 RAG (Retrieval-Augmented Generation) 실습 가이드

이 예제는 **RAG(검색 증강 생성)**의 핵심 원리를 5단계로 나누어 설명합니다. 대규모 언어 모델(LLM)이 배우지 못한 최신 정보나 특정 도메인의 지식을 검색하여 답변의 정확도를 높이는 과정을 학습합니다.

---

## 🛠️ 주요 실습 내용
1. **임베딩(Embedding)**: 텍스트를 숫자로 변환하여 의미적 유사도를 계산합니다.
2. **Top-K Retrieval**: 수많은 데이터 중 질문과 가장 관련 있는 상위 $K$개의 데이터를 찾아냅니다.
3. **Context Injection**: 찾아낸 정보를 LLM의 프롬프트에 주입하여 답변을 유도합니다.

---

## 💻 실습 코드 (`05_RAG_inmemory.py`)

```python
import ollama
import numpy as np

# RAG의 5단계 프로세스를 시각화하여 학생들이 이해하기 쉽게 구성합니다.

# 1. [Step 1] 지식 베이스(Knowledge Base) 준비
# LLM이 학습하지 않았을 수 있거나, 최신 정보를 제공하기 위한 데이터들입니다.
documents = [
    "수성은 태양과 가장 가까운 행성으로 낮에는 매우 뜨겁고 밤에는 매우 춥습니다.",
    "금성은 두꺼운 이산화탄소 대기 때문에 태양계에서 가장 뜨거운 행성입니다.",
    "지구는 액체 상태의 물이 존재하며 생명체가 살고 있는 유일한 행성입니다.",
    "화성은 표면의 산화철 성분 때문에 '붉은 행성'이라고 불립니다.",
    "목성은 태양계에서 가장 큰 행성으로, 거대한 태풍인 '대적점'이 있습니다.",
    "토성은 얼음과 먼지로 이루어진 아름답고 거대한 고리를 가지고 있습니다.",
    "천왕성은 자전축이 옆으로 완전히 누워 있는 독특한 행성입니다.",
    "해왕성은 태양계의 가장 바깥쪽에 위치한 차가운 가스 행성입니다.",
    "명왕성은 과거 행성이었으나 현재는 왜소행성으로 분류됩니다.",
    "달은 지구의 유일한 자연 위성으로 인류가 직접 발을 디딘 곳입니다."
]

model = 'qwen3:8b'

print(f"--- [Step 1] 총 {len(documents)}개의 문서를 지식 베이스에 등록했습니다. ---")

# 2. [Step 2] 문서 임베딩(Embedding) 생성
# 텍스트를 AI가 이해할 수 있는 숫자 벡터로 변환하여 '벡터 저장소'를 구축하는 단계입니다.
print(f"--- [Step 2] 각 문서의 임베딩(벡터화)을 생성 중입니다... ---")
doc_embeddings = [ollama.embeddings(model=model, prompt=doc)['embedding'] for doc in documents]
print(f"    (완료: {len(doc_embeddings)}개의 벡터 생성)")

# 3. [Step 3] 사용자 질문 및 질문 임베딩
query = "태양계에서 가장 뜨거운 행성은 무엇이고, 고리가 있는 행성은 무엇인가요?"
print(f"
--- [Step 3] 사용자 질문: "{query}" ---")
query_emb = ollama.embeddings(model=model, prompt=query)['embedding']

# 4. [Step 4] 유사도 검색 (Retrieval)
# 코사인 유사도를 계산하여 질문과 가장 관련성이 높은 상위 3개 문서를 찾습니다.
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print(f"--- [Step 4] 질문과 유사한 문서를 찾는 중 (Top-3 Retrieval)... ---")
similarities = [cosine_similarity(query_emb, doc_emb) for doc_emb in doc_embeddings]

# 상위 3개의 인덱스 추출
top_k = 3
top_indices = np.argsort(similarities)[-top_k:][::-1]

retrieved_docs = [documents[i] for i in top_indices]

for i, idx in enumerate(top_indices):
    print(f"    검색된 결과 {i+1}: (유사도: {similarities[idx]:.4f}) {documents[idx]}")

# 5. [Step 5] 증강된 프롬프트 주입 및 답변 생성 (Generation)
# 검색된 정보를 LLM에게 전달하여 '근거'에 기반한 답변을 유도합니다.
print(f"
--- [Step 5] 검색된 정보를 바탕으로 LLM이 답변을 생성 중입니다... ---")

# 검색된 문서들을 하나의 텍스트로 합칩니다.
context = "
".join(retrieved_docs)

response = ollama.chat(model=model, messages=[
    {
        'role': 'system', 
        'content': f"당신은 친절한 과학 선생님입니다. 아래 제공된 [참고 자료]를 바탕으로만 답변해 주세요.

[참고 자료]:
{context}"
    },
    {'role': 'user', 'content': query}
])

print("
" + "="*50)
print("최종 답변:")
print(response['message']['content'])
print("="*50)
```

---

## 📋 핵심 요약
- **Retrieval**: 방대한 데이터 중 질문과 관계있는 조각을 찾는 과정.
- **Augmentation**: 검색된 조각을 질문과 함께 묶어 프롬프트를 풍부하게 만드는 과정.
- **Generation**: 보강된 정보를 바탕으로 답변을 만들어내는 과정.

이 방식은 환각(Hallucination) 현상을 줄이고, 최신 정보를 반영하는 데 매우 효과적입니다.

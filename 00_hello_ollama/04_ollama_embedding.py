# 4. 임베딩(Embedding) 생성하기
# ollama.embeddings()로 얻은 벡터는 텍스트의 의미를 숫자로 표현한 것으로, 주로 다음과 같은 보조 작업에 사용됩니다:
# - 유사도 검색 (예: 질문과 가장 비슷한 문서 찾기)
# - 클러스터링/분류 (텍스트를 주제별로 그룹화)
# - 검색 증강 생성(RAG) – 사용자 질문을 임베딩으로 변환 → 벡터 DB에서 유사 문서 검색 → 검색된 문서를 프롬프트에 포함시켜 LLM에 전달

import ollama

embeddings = ollama.embeddings(model='qwen3:8b', prompt='임베딩을 생성할 문장')
print(embeddings['embedding'])  # 숫자 리스트 출력
print(len(embeddings['embedding']))
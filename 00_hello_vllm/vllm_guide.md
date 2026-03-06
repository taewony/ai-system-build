

# 서버 실행
python -m vllm.entrypoints.openai.api_server \
    --model deepseek-ai/deepseek-coder-7b-instruct-v1.5 \
    --port 8000

    서버 실행 (터미널 1): 질문하신 python -m vllm.entrypoints... 명령어를 실행하여 서버가 Uvicorn running on http://0.0.0.0:8000 메시지를 띄울 때까지 기다립니다.

클라이언트 실행 (터미널 2): 서버가 켜진 상태에서 새 터미널을 열어 가상환경을 활성화한 후 다음을 실행합니다.

python hello_vllm.py

OpenAI 호환성
vLLM은 OpenAI API 규격을 그대로 따르기 때문에, 기존에 OpenAI 라이브러리로 짜인 수많은 앱(LangChain, AutoGPT 등)을 코드 수정 거의 없이 로컬 모델로 교체할 수 있다는 점이 큰 장점입니다.
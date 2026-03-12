# 패키지 임포트 테스트
import importlib.metadata

try:
    import ollama
    version = importlib.metadata.version("ollama")
    print(f"✅ ollama 패키지 버전: {version}")
except Exception as e:
    print(f"⚠️ 버전 확인 실패: {e}")

try:
    import anthropic
    print("✅ anthropic 패키지 설치 확인됨, 버전:", anthropic.__version__)
except Exception as e:
    print("❌ anthropic 임포트 실패:", e)

try:
    import openai
    print("✅ openai 패키지 설치 확인됨, 버전:", openai.__version__)
except Exception as e:
    print("❌ openai 임포트 실패:", e)
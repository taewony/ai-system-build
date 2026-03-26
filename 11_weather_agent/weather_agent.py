import streamlit as st
import anthropic
import requests
from datetime import datetime
import time

# ============================================
# 1. 에이전트 도구(Tools) 정의
# ============================================
def get_my_location():
    """IP 기반 위치 파악"""
    try:
        res = requests.get("http://ip-api.com/json/").json()
        return f"{res.get('city', '알 수 없는 도시')}, {res.get('country', '알 수 없는 국가')}"
    except Exception:
        return "Daejeon, South Korea"

def get_today():
    """오늘 날짜 확인"""
    return datetime.now().strftime("%Y년 %m월 %d일 %A")

def get_weather(city):
    """현재 날씨 가져오기 (MOCK 데이터 - 현재 사용 중)"""
    return f"{city}의 현재 날씨는 '약간 흐림', 기온은 15도, 강수 확률 20%입니다."

# 🌟 [새로 추가된 함수] 실제 날씨 API 연동 함수
def get_real_weather(city: str, api_key: str) -> str:
    """
    OpenWeatherMap API를 사용하여 실제 날씨를 가져옵니다.
    사용법: 회원가입 후 발급받은 api_key를 인자로 넘겨주세요.
    """
    if not api_key:
        return f"⚠️ {city}의 날씨를 조회할 수 없습니다. (API 키 필요)"
    
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric", # 섭씨 온도로 변환
        "lang": "kr"       # 한국어로 상태 설명 받기
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # 에러 발생 시 예외 처리
        data = response.json()
        
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        
        return f"{city}의 현재 날씨는 '{weather_desc}', 기온은 {temp}도, 습도는 {humidity}%입니다."
    except Exception as e:
        return f"🚨 {city} 날씨 API 호출 실패: {e}"

# ============================================
# 2. 에이전트 코어: Anthropic API (Ollama)
# ============================================
def run_weather_agent(system_instruction: str):
    client = anthropic.Anthropic(base_url='http://localhost:11434', api_key='ollama')
    
    with st.status("에이전트가 정보를 수집하고 있습니다...", expanded=True) as status:
        st.write("🌍 IP 기반 현재 위치 파악 중...")
        time.sleep(1) 
        location = get_my_location()
        st.write(f"📍 위치 확인 완료: {location}")
        
        st.write("📅 날짜 정보 동기화 중...")
        today = get_today()
        
        st.write("🌤️ 기상청 레이더 스캔 중...")
        time.sleep(1)
        
        # 💡 [직접 수정할 부분] 나중에 실제 API를 쓸 때는 아래 줄을 주석 처리하고
        weather_info = get_weather(location)
        # 💡 아래 코드를 활성화하세요 (발급받은 API 키 입력)
        # my_api_key = "여기에_OpenWeatherMap_API_키_입력"
        # weather_info = get_real_weather(location, my_api_key)
        
        st.write(f"📡 날씨 데이터 획득: {weather_info}")
        
        status.update(label="날씨 정보 분석 완료. 에이전트가 브리핑을 준비 중이니 조금만 더 기다려 주세요", state="complete", expanded=False)
    
    prompt = f"""
    오늘 날짜: {today}
    사용자 위치: {location}
    날씨 정보: {weather_info}
    
    이 정보를 바탕으로 사용자에게 재미있는 날씨 브리핑과 어울리는 옷차림(OOTD)을 추천해줘.
    """
    
    try:
        message = client.messages.create(
            model='qwen2.5:7b',
            max_tokens=1024,
            system=system_instruction,
            messages=[{'role': 'user', 'content': prompt}]
        )
        return message.content[0].text, location
    except Exception as e:
        return f"🚨 에이전트 통신 오류: {str(e)}", location

# ============================================
# 3. Streamlit UI
# ============================================
def main():
    st.set_page_config(page_title="바이브 체크 날씨 에이전트", page_icon="🌦️", layout="centered")
    
    st.title("🌦️ 바이브 체크 날씨 에이전트")
    st.markdown("단조로운 날씨 정보는 그만! 에이전트가 위치를 자동 파악해 당신의 **'바이브'**에 맞는 맞춤형 기상 특보를 전해드립니다.")
    
    st.divider()
    
    # UI 제어: 페르소나 선택
    persona = st.radio(
        "🎙️ 오늘 당신에게 날씨를 알려줄 에이전트는?",
        ["츤데레 할머니", "하드보일드 탐정", "오두방정 호들갑 요정"],
        horizontal=True
    )
    
    # 💡 프롬프트 딕셔너리를 밖으로 빼서, 라디오 버튼 선택 즉시 변경되도록 구조 수정
    persona_prompts = {
        "츤데레 할머니": "너는 무뚝뚝하지만 손주를 끔찍이 아끼는 경상도 할머니야. 날씨 정보를 바탕으로 옷차림이나 밥 챙겨 먹으라는 잔소리를 찰지게 해줘.",
        "하드보일드 탐정": "너는 1950년대 누아르 영화에 나오는 시니컬한 사립 탐정이야. 비가 오든 맑든 세상은 어둡다고 불평하면서 날씨 정보를 담담하게 읊어줘.",
        "오두방정 호들갑 요정": "너는 텐션이 1000%인 요정이야! 날씨가 어떻든 너무 신나서 이모티콘을 남발하며 오늘의 럭키 아이템과 날씨를 소개해줘."
    }
    
    system_instruction = persona_prompts.get(persona, "너는 친절한 날씨 안내원이야.")
    
    # 💡 버튼 밖으로 이동: 사용자가 버튼을 누르기 전에도 확인 가능!
    st.info(f"**💡 현재 주입된 시스템 프롬프트:**\n\n`{system_instruction}`")
    
    if st.button("🚀 오늘의 날씨 & 바이브 체크하기", type="primary", use_container_width=True):
        report, loc = run_weather_agent(system_instruction)
        
        st.subheader("📬 에이전트의 메시지가 도착했습니다")
        with st.container(border=True):
            st.markdown(f"**수신 지역**: `{loc}`")
            st.markdown("---")
            st.write(report)

if __name__ == "__main__":
    main()
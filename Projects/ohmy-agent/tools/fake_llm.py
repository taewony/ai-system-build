import json

class FakeMessage:
    def __init__(self, content):
        self.content = content

class FakeChoice:
    def __init__(self, content):
        self.message = FakeMessage(content)

class FakeCompletions:
    def __init__(self):
        self.step = 0

    def create(self, model, messages, **kwargs):
        self.step += 1
        
        # 1단계: 사용자 입력을 받고 지식을 파일로 저장하려는 액션 반환
        if self.step == 1:
            reply = {
                "thought": "사용자의 요청을 처리하기 위해 중요한 지식을 파일로 먼저 저장해두자.",
                "tool": "write_knowledge",
                "args": {"filename": "ai_memory.txt", "content": "Streamlit과 에이전트 루프는 yield로 연결하면 아주 좋습니다."}
            }
        
        # 2단계: 저장했던 지식을 다시 읽어오려는(검색) 액션 반환
        elif self.step == 2:
            reply = {
                "thought": "방금 저장한 지식 파일이 잘 있는지 확인하고, 그 내용을 바탕으로 대답을 준비하자.",
                "tool": "read_knowledge",
                "args": {"filename": "ai_memory.txt"}
            }
            
        # 3단계: 루프 종료 및 최종 답변 반환
        else:
            reply = {
                "thought": "지식 검색을 마쳤으니 최종 답변을 제공하자.",
                "tool": "finish",
                "args": {"message": "에이전트가 워크스페이스에 지식을 저장하고 다시 읽어오는 데 성공했습니다!"}
            }
            self.step = 0 # 다음 대화를 위해 초기화
            
        return type('FakeResponse', (), {'choices': [FakeChoice(json.dumps(reply, ensure_ascii=False))]})()

class FakeClient:
    """OpenAI API client.chat.completions.create 구조를 그대로 모방한 클래스"""
    def __init__(self):
        self.chat = type('Chat', (), {'completions': FakeCompletions()})()
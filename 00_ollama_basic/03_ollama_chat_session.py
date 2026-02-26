# 3. 대화 맥락 유지하기

import ollama

model = 'qwen2.5:7b'
messages = []

while True:
    
    user_input = input("You: ")
    messages.append({'role': 'user', 'content': user_input})

    response = ollama.chat(model=model, messages=messages)
    assistant_message = response['message']['content']
    print(f"Assistant: {assistant_message}")
    
    messages.append({'role': 'assistant', 'content': assistant_message})
    # print(f"Messages: {messages}")
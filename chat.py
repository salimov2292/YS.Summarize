import requests
import json
from config import URL_CHAT, CONTENT_TYPE_JSON

def make_chat_request(access_token):
    payload = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "user",
                "content": "Сколько будет 2+2?"
            }
        ],
        "temperature": 1,
        "top_p": 0.1,
        "n": 1,
        "stream": False,
        "max_tokens": 512,
        "repetition_penalty": 1
    }
    
    headers = {
        'Content-Type': CONTENT_TYPE_JSON,
        'Accept': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(URL_CHAT, headers=headers, data=json.dumps(payload), verify=False)  # Отключаем проверку сертификата
    response.raise_for_status()  # Проверка на ошибки
    return response.json()

def print_chat_response(chat_data):
    choices = chat_data.get("choices", [])
    if choices and "message" in choices[0]:
        print(choices[0]["message"]["content"])
    else:
        print("Ответ не содержит поле 'content'")

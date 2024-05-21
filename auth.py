import requests
import uuid
from config import CERTIFICATE_PATH, URL_TOKEN, AUTHORIZATION_HEADER, SCOPE, CONTENT_TYPE_FORM

def get_access_token():
    headers = {
        'Content-Type': CONTENT_TYPE_FORM,
        'Accept': 'application/json',
        'RqUID': str(uuid.uuid4()),  # Генерация уникального RqUID
        'Authorization': AUTHORIZATION_HEADER
    }
    response = requests.post(URL_TOKEN, headers=headers, data=SCOPE, verify=CERTIFICATE_PATH)
    response.raise_for_status()  # Проверка на ошибки
    token_data = response.json()
    return token_data.get('access_token')

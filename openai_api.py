import requests
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем ключ API из переменной окружения
api_key = os.getenv('AI_API_KEY')

# Заголовки для авторизации и указания типа контента
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json',
}

def get_openai_response(user_input, user_username=None, user_id=None):
    """
    Функция для отправки запроса в OpenAI и получения ответа.
    
    :param user_input: Ввод пользователя для запроса
    :param user_username: (опционально) Юзернейм пользователя
    :param user_id: (опционально) ID пользователя
    :return: Ответ от OpenAI
    """
    # Создаем сообщение для системы
    system_message = 'You are a helpful assistant.'

    # Формируем данные для запроса
    messages = [{'role': 'system', 'content': system_message}]
    
    # Если передан запрос от пользователя, добавляем его
    messages.append({'role': 'user', 'content': user_input})
    
    # Если есть информация о пользователе, добавляем ее в контекст
    if user_username and user_id:
        messages.append({'role': 'system', 'content': f"User info - Username: {user_username}, ID: {user_id}"})
    
    data = {
        'model': 'gpt-3.5-turbo',  # Модель, которая используется
        'messages': messages,
    }

    url = 'https://openrouter.ai/api/v1/chat/completions'

    # Отправляем POST-запрос
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Генерирует исключение для статусов ошибок HTTP

        result = response.json()
        if 'choices' in result:
            return result['choices'][0]['message']['content']
        else:
            return "Ошибка: Ответ не найден в API."

    except requests.exceptions.RequestException as err:
        return f"Ошибка запроса: {err}"
import logging
from telegram import Update
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def get_user_info(update: Update, log=True):
    """
    Получает информацию о пользователе: username и ID.
    Также может логировать информацию, если log=True.

    Аргументы:
    - update: Объект обновления от Telegram, содержащий информацию о сообщении.
    - log: Если True, будет происходить логирование информации о пользователе.

    Возвращает:
    - user_username: username пользователя или ID, если username отсутствует.
    - user_id: ID пользователя.
    """
    try:
        # Получаем пользователя из обновления
        user = update.message.from_user
        # Получаем username или ID пользователя
        user_username = user.username if user.username else f"ID:{user.id}"  # Если username отсутствует, используем ID
        user_id = user.id

        # Логируем информацию, если нужно
        if log:
            logger.info(f"Получена информация о пользователе: @{user_username} (ID: {user_id})")

        return user_username, user_id

    except AttributeError as e:
        # Логируем ошибку, если возникла проблема с получением данных
        logger.error("Ошибка при получении информации о пользователе.", exc_info=e)
        return None, None

# Получение API-ключа из переменных окружения .env (если это необходимо)
api_key = os.getenv('AI_API_KEY')

def get_openai_response(user_input, user_id, user_username):
    """
    Отправляет запрос к API OpenAI с переданным пользовательским запросом.
    Также логирует запрос с использованием информации о пользователе.

    Аргументы:
    - user_input: запрос пользователя.
    - user_id: ID пользователя.
    - user_username: username пользователя.
    """
    # Логируем запрос с пользователем
    logger.info(f"Получен запрос от @{user_username} (ID: {user_id}): {user_input}")
    
    # Пример данных для запроса к OpenAI
    data = {
        'model': 'gpt-3.5-turbo', 
        'messages': [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': user_input},
        ],
    }

    url = 'https://openrouter.ai/api/v1/chat/completions'

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json',
    }

    try:
        # Отправляем запрос
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        return result.get('choices', [{}])[0].get('message', {}).get('content', "Не получен ответ от API.")
    except requests.exceptions.RequestException as err:
        logger.error(f"Ошибка запроса к API: {err}")
        return f"Ошибка запроса: {err}"
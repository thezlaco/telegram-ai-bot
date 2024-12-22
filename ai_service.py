import aiohttp
import logging
from dotenv import load_dotenv
import os

# Загружаем переменные окружения из .env файла
load_dotenv()

# Настройка логирования
logger = logging.getLogger(__name__)

# Параметры запроса к API
params = {
    'max_tokens': 2000,  # Ограничиваем количество токенов
    'temperature': 1.0,  # Настройка на креативность
    'top_p': 1.0,  # Гибкость в ответах
    'frequency_penalty': 1.4,  # Ограничение частоты повторений слов
    'presence_penalty': 0.8,  # Ограничение повторов идей
    'stop': None,  # Строка или список строк, на которых модель прекратит генерацию текста.
    'best_of': 1,  # Генерирует несколько завершений для каждого запроса и возвращает наилучшее.
    'logprobs': None,  # Возвращает вероятность каждого токена в ответе.
    'echo': False,  # Если True, в ответе будет также возвращаться исходный запрос.
    'n': 1,  # Количество вариантов ответов, которые должны быть сгенерированы.
    'stream': False,  # Если True, будет использоваться потоковый режим для получения результата по мере его формирования.
    'user': None,  # Идентификатор пользователя для привязки данных.
    'logit_bias': None,  # Регулирует вероятность использования определенных токенов в ответах.
}

# Получаем токены из .env
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('API_KEY')

# Телеграмм Бот API
API_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'

# Функция для получения сообщений
async def get_updates():
    url = f'{API_URL}getUpdates'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

# Функция для отправки сообщений
async def send_message(chat_id, text):
    url = f'{API_URL}sendMessage'
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            response.raise_for_status()
            return await response.json()

# Функция для получения ответа от ИИ
async def get_ai_response(user_message, API_KEY, user_username=None, user_id=None):
    """
    Получает ответ от внешнего ИИ, используя сообщение пользователя и API-ключ.

    Аргументы:
    - user_message: сообщение от пользователя.
    - API_KEY: API-ключ для доступа к ИИ.
    - user_username: (опционально) username пользователя.
    - user_id: (опционально) ID пользователя.

    Возвращает:
    - Ответ от API или сообщение об ошибке.
    """
    # Логируем данные пользователя, если они присутствуют
    if user_username and user_id:
        logger.info(f"Запрос от пользователя: @{user_username} (ID: {user_id})")

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json',
    }

    # Формируем тело запроса для модели
    data = {
        'model': 'gpt-3.5-turbo',  # Указываем модель
        'messages': [{'role': 'user', 'content': user_message}],
        **params  # Добавляем параметры запроса
    }

    # URL API для запроса
    url = 'https://openrouter.ai/api/v1/chat/completions'

    try:
        # Выполняем запрос к API
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                response.raise_for_status()  # Проверяем статус ответа
                result = await response.json()

                # Проверка на наличие ответа от модели
                if 'choices' in result:
                    return result['choices'][0]['message']['content']
                else:
                    logger.error(f"API не вернул ожидаемый результат: {result}")
                    return "Ошибка: не получен ответ от API."
    except aiohttp.ClientError as err:
        logger.error(f"Ошибка запроса: {err}")
        return f"Ошибка при запросе: {err}"
    except Exception as err:
        logger.error(f"Произошла ошибка: {err}")
        return f"Произошла ошибка: {err}"

# Основная функция для получения сообщений и обработки их
async def handle_messages():
    updates = await get_updates()
    if updates['ok'] and updates['result']:
        for update in updates['result']:
            user_message = update.get('message', {}).get('text', '')
            user_id = update.get('message', {}).get('from', {}).get('id', '')
            user_username = update.get('message', {}).get('from', {}).get('username', None)

            # Логируем, что получено новое сообщение
            logger.info(f"Новое сообщение от @{user_username} (ID: {user_id}): {user_message}")

            # Отправляем сообщение в ИИ
            response = await get_ai_response(user_message, API_KEY, user_username, user_id)

            # Отправляем ответ обратно пользователю
            chat_id = update.get('message', {}).get('chat', {}).get('id')
            await send_message(chat_id, response)

# Запуск обработки сообщений
if __name__ == '__main__':
    import asyncio
    asyncio.run(handle_messages())
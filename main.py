from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackContext, filters
import os
from dotenv import load_dotenv
import logging
from user_logger import get_user_info  # Импортируем get_user_info из user_logger
from ai_service import get_ai_response  # Импортируем внешний ИИ

# Загружаем переменные окружения из .env файла
load_dotenv()

# Токен вашего бота и API-ключ для внешнего ИИ
TOKEN = os.getenv('TELEGRAM_TOKEN')
API_KEY = os.getenv('AI_API_KEY')

# Настроим базовое логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Проверка наличия токенов
if not TOKEN or not API_KEY:
    logger.error("TELEGRAM_TOKEN и AI_API_KEY должны быть установлены в переменных окружения.")
    exit(1)

async def handle_error(update: Update, error_message: str) -> None:
    """
    Универсальная функция для обработки ошибок и отправки сообщений об ошибке.
    """
    logger.error(error_message)
    await update.message.reply_text('Произошла ошибка, попробуйте позже.')

async def start(update: Update, context: CallbackContext) -> None:
    """
    Обрабатывает команду /start, логирует данные пользователя и отправляет приветственное сообщение.
    """
    try:
        # Извлекаем информацию о пользователе при каждом сообщении
        user_username, user_id = get_user_info(update)
        logger.info(f"User info: {user_username}, ID: {user_id}")

        # Сохраняем информацию о пользователе в контексте
        context.user_data['username'] = user_username
        context.user_data['user_id'] = user_id

        await update.message.reply_text(f'Привет, {user_username} 😏')

    except Exception as e:
        await handle_error(update, f"Ошибка при обработке команды /start: {e}")

async def respond(update: Update, context: CallbackContext) -> None:
    """
    Обрабатывает текстовые сообщения, логирует данные пользователя и запрашивает ответ от ИИ.
    """
    try:
        # Извлекаем данные пользователя при каждом сообщении
        user_username = context.user_data.get('username', None)
        user_id = context.user_data.get('user_id', None)

        logger.info(f"User info: {user_username}, ID: {user_id}")

        # Получаем ответ от внешнего ИИ, передавая информацию о пользователе
        ai_response = await get_ai_response(update.message.text, API_KEY)

        # Опционально добавляем информацию о пользователе в ответ
        if user_username and user_id:
            ai_response = f"@{user_username} (ID: {user_id}):\n{ai_response}"

        await update.message.reply_text(ai_response)

    except Exception as e:
        await handle_error(update, f"Ошибка при обработке сообщения: {e}")

async def get_username(update: Update, context: CallbackContext) -> None:
    """
    Функция для обработки запроса юзернейма. Извлекает и возвращает юзернейм пользователя.
    """
    try:
        user_username = context.user_data.get('username', None)

        if user_username:
            response_text = f'Ваш юзернейм: @{user_username}'
        else:
            response_text = "Извините, я не могу узнать ваш юзернейм."

        await update.message.reply_text(response_text)

    except Exception as e:
        await handle_error(update, f"Ошибка при получении юзернейма: {e}")

def main():
    """
    Основная функция для запуска бота. Регистрирует обработчики команд и сообщений.
    """
    application = Application.builder().token(TOKEN).build()

    # Регистрируем обработчики команд и сообщений
    application.add_handler(CommandHandler('start', start))  # Обработчик команды /start
    application.add_handler(CommandHandler('username', get_username))  # Обработчик команды для получения юзернейма
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, respond))  # Обработчик сообщений

    # Запускаем бота
    application.run_polling()

if __name__ == '__main__':
    main()
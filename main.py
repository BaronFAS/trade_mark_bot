import os
import telegram
import logging

from time import sleep
from dotenv import load_dotenv
from telegram.error import NetworkError, Unauthorized


load_dotenv()

UPDATE_ID = None
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
# TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

MESSAGE = {
    'start': 'Привет, я @gardium_tm_bot.',
    'new_search': '🚀 Введите название, которое вы хотели бы проверить',
}


def init_logger() -> None:
    """Логируем проект."""
    pass


def check_tokens() -> bool:
    """Проверяет доступность токенов в переменных окружения.
    Прекращает работу бота если их нет.
    """
    pass


def send_request_to_api_web() -> list[str]:
    """Посылает пост запрос и получает ответ от api."""
    pass


def check_result_search_tm() -> None:
    """Проверяет поступившие данные и записывает их."""
    pass


def incoming_message() -> str:
    """Получает сообщение от пользователя."""
    pass


def send_message(bot: telegram.bot.Bot, message: str) -> None:
    """Отправляет пользователю сообщение."""
    global UPDATE_ID

    for update in bot.get_updates(offset=UPDATE_ID, timeout=10):
        UPDATE_ID = update.update_id + 1
        if update.message:
            # не все сообщения содержат текст
            if update.message.text:
                # Ответ на сообщение
                update.message.reply_text(f'Вы написали: {update.message.text}')
                update.message.reply_text(f'Бот говорит: {message}')


def send_data_to_webhook_crm() -> None:
    """Отправляет данные пользователя в CRM."""
    pass


def main() -> None:
    """Основная логика работы бота."""
    global UPDATE_ID
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    try:
        UPDATE_ID = bot.get_updates()[0].update_id
    except IndexError:
        UPDATE_ID = None
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    while True:
        sleep(1)
        try:
            send_message(bot, MESSAGE['start'])
        except NetworkError:
            # ошибка сети, ждем 5 секунд
            sleep(5)
        except Unauthorized:
            # Пользователь удалил или заблокировал бота.
            UPDATE_ID += 1


if __name__ == '__main__':
    main()

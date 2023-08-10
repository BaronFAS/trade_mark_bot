import os
import telegram

from dotenv import load_dotenv


load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def init_logger() -> None:
    """Логируем проект."""
    pass


def check_tokens() -> bool:
    """Проверяет доступность токенов в переменных окружения.
    Прекращает работу бота если их нет.
    """
    pass


def read_input() -> str:
    """Получает сообщение от пользователя."""
    pass


def send_request_to_api_web() -> list[str]:
    """Посылает пост запрос и получает ответ от api."""
    pass


def check_result_search_tm() -> None:
    """Проверяет поступившие данные и записывает их."""
    pass


def send_message(bot: telegram.bot.Bot, message: str) -> None:
    """Отправляет пользователю сообщение."""
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)


def send_data_to_webhook_crm() -> None:
    """Отправляет данные пользователя в CRM."""
    pass


def main() -> None:
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    message = 'Привет, я @gardium_tm_bot.'
    send_message(bot, message)


if __name__ == "__main__":
    main()

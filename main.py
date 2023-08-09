import os

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


def check_result_search_tm() -> Dict[str]:
    """Проверяет поступившие данные и записывает их."""
    pass


def send_message() -> None:
    """Отправляет пользователю сообщение."""
    pass


def send_data_to_webhook_crm() -> None:
    """Отправляет данные пользователя в CRM."""
    pass


def main() -> None:
    """Основная логика работы бота."""
    pass


if __name__ == '__main__':
    main()

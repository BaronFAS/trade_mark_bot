import logging
import os
import telegram
import sys
import requests
from http import HTTPStatus
from typing import List  # Dict
from dotenv import load_dotenv
from pprint import pprint
from time import sleep
from telegram.error import NetworkError, Unauthorized

load_dotenv()

API_ENDPOINT = os.getenv('API_ENDPOINT')
UPDATE_ID = None
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
# TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

MESSAGE = {
    'start': 'Привет, я @gardium_tm_bot.',
    'new_search': '🚀 Введите название, которое вы хотели бы проверить',
}


HEADERS = {
    "Content-Type": f"{os.getenv('CONTENT_TYPE')}",
    "X-Requested-With": f"{os.getenv('X_REQUESTED_WITH')}",
    "Authorization": f"{os.getenv('AUTHORIZATION')}"
}

logging.basicConfig(
    level=logging.DEBUG,
    filename='main_log',
    filemode='w',
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8',
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def init_logger() -> None:
    """Логируем проект."""
    pass


def check_tokens() -> bool:
    """Проверяет доступность токенов в переменных окружения.
    Прекращает работу бота если их нет.
    """
    pass


def read_input(s) -> str:
    """Получает сообщение от пользователя."""
    input_data = s
    return input_data


def send_request_to_api_web(message: str) -> List[str]:
    """Посылает пост запрос и получает ответ от api."""
    input_data = message
    data = "type=generate&data[queryText]="+input_data+"&sync=true"
    try:
        response = requests.post(
            url=API_ENDPOINT,
            headers=HEADERS,
            data=data.encode('utf-8'))
        logger.debug(f'К API Гардиум отправлен запрос: {input_data}.')

    except Exception as error:
        error_text = f'Ошибка при запросе к API: {error}.'
        logger.error(error_text)
        raise ValueError(error_text)

    finally:
        logger.info('Функция send_request_to_api_web выполнена.')
    if response.status_code != HTTPStatus.OK:
        error_text = (
            'Ошибочный ответ от сервиса '
            f'Гардиум: {response.status_code}'
        )
        logger.error(error_text)
        raise ValueError(error_text)

    logger.debug(f'От API Гардиум получен ответ: {response.json()}.')
    print(response.json())
    # return response.json()
    pprint(response.json())


def check_result_search_tm():  # -> Dict[str]:
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
                send_request_to_api_web(update.message.text)


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
    # send_request_to_api_web()
    main()

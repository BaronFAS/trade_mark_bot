import logging
import os
import sys
import requests
from http import HTTPStatus
from typing import List  # Dict
from dotenv import load_dotenv

load_dotenv()

API_ENDPOINT = os.getenv('API_ENDPOINT')
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


def read_input() -> str:
    """Получает сообщение от пользователя."""
    pass


def send_request_to_api_web() -> List[str]:
    """Посылает пост запрос и получает ответ от api."""
    # input_data = str(input())
    input_data = 'Гарант'
    data = {"query": "type=generate&data[queryText]=Гарант&sync=true"}
    try:
        response = requests.post(
            url=API_ENDPOINT,
            headers=HEADERS,
            data=data)
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


def check_result_search_tm():  # -> Dict[str]:
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
    send_request_to_api_web()

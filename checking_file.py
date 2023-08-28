import os
import telegram
import requests
import re
import time
import json

from typing import Dict, Union
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)
from dotenv import load_dotenv
# from http import HTTPStatus
from telegram.update import Update

from logging_config import logger
from message_config import MESSAGES, TECH_MESSAGES, RESULTS_CHECK

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
API_ENDPOINT = os.getenv("API_ENDPOINT")
# CRM_ENDPOINT = "https://webhook.site/cae8a46f-b79e-480d-8353-ddd6fb0db130"
CRM_ENDPOINT = "https://webhook.site/#!/cae8a46f-b79e-480d-8353-ddd6fb0db130/30d7ba1b-4b51-43a2-b1ff-8faa9c745d40/1"

API_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "X-Requested-With": "XMLHttpRequest",
    "Authorization": f"{os.getenv('AUTHORIZATION')}",
}
CRM_HEADERS = {"Content-Type": "application/json"}

TM_NAME = None
"""Хранит название которые пользователь ввел для проверки."""
# Может стоит сделать списком и хранить историю проверок?

"""Создаем экземпляр бота."""
BOT = telegram.Bot(token=TELEGRAM_TOKEN)


def create_crm_data(user_general: Dict) -> Dict:
    current_time = time.time()
    crm_data = {
        "direction": "000000178",
        "type": "2",
        "name": user_general["first_name"],
        "phone": "",
        "comment": "Название для проверки: " + TM_NAME,
        "timestamp": current_time,
        "clientId": "",
        "utmContent": "search_trade_mark_bot",
        "utmCampaign": "bot",
        "utmSource": "telegram",
    }
    logger.info("Функция create_crm_data выполнена.")
    return crm_data


def check_response(response: Dict[str, Union[int, str, bool]]) -> bool:
    if not isinstance(response["id"], int):
        logger.warning("Ошибка API, ID должен быть int")
        return False
    if not isinstance(response["urlCheck"], str):
        logger.warning("Ошибка API, urlCheck должен быть str")
        return False
    if not isinstance(response["resultCheck"], str):
        logger.warning("Ошибка API, resultCheck должен быть str")
        return False
    if not response["resultCheck"] in RESULTS_CHECK:
        logger.warning("Ошибка API, в resultCheck нет нужного ключа")
        return False
    if response["resultCheck"] == "false":
        logger.warning("Ошибка API, resultCheck = false")
        return False
    logger.info("Полученный json от API правильный")
    return True


def create_answer(response) -> str:
    url_for_analytics = response["urlCheck"] + "?full=true&utmSource=telegram"
    match response["resultCheck"]:
        case "High":
            answer = RESULTS_CHECK["High"] + url_for_analytics
            logger.debug("Результаты проверки по High")
        case "Medium":
            logger.debug("Результаты проверки по Medium")
            answer = RESULTS_CHECK["Medium"] + url_for_analytics
        case "Low":
            logger.debug("Результаты проверки по Low или None")
            answer = RESULTS_CHECK["Low"] + url_for_analytics
        case "None":
            logger.debug("Результаты проверки по Low или None")
            answer = RESULTS_CHECK["None"] + url_for_analytics
        case _:
            logger.warning("Ошибка в результатах проверки")
            answer = TECH_MESSAGES["api_error"]
    logger.info("Функция create_answer выполнена.")
    return answer


def check_message(input_data: str) -> bool:
    """Посылает пост запрос и получает ответ от api."""
    if re.fullmatch(r"^[\w\d_\-=.,]{1,100}$", input_data):
        logger.debug("Запрос соответствует параметрам.")
        return True
    return False


# def send_request(url: str, headers: dict, data: str):
#     """Посылает post запрос и получает ответ."""
#     try:
#         response = requests.post(
#             url=url,
#             headers=headers,
#             data=data)
#         response.raise_for_status()
#         logger.debug(f"response: {response.raise_for_status()}.")

#         try:
#             if response.status_code != 204:
#                 response_json = response.json()
#                 return response_json
#             # response_json = response.json()
#         except json.JSONDecodeError as error:
#             logger.error(f"Ошибка декодирования JSON: {error}")
#             raise ValueError(f"Ошибка декодирования JSON: {error}")

#         logger.debug(f"Отправлен post запрос: {data}.")
#         logger.debug(f"Получен ответ: {response.json()}.")

#         if not response_json:
#             logger.warning("Получен пустой ответ от API")
#             return None

#     except requests.exceptions.RequestException as error:
#         error_text = f"Ошибка при запросе: {error}."
#         logger.error(error_text)
#         raise ValueError(error_text)
#     # else:
#     logger.info("Функция send_request выполнена.")
#     # return response.json()
#     return response_json


def send_request(url: str, headers: dict, data: str):
    """Посылает post запрос и получает ответ."""
    try:
        response = requests.post(
            url=url,
            headers=headers,
            data=data)
        if response.status_code != 204:
            response_json = response.json()
            logger.debug(f"Отправлен post запрос: {data}.")
            logger.debug(f"Получен ответ: {response_json}.")
            if not response_json:
                logger.warning("Получен пустой ответ от API")
                return None
            return response_json
    except requests.exceptions.RequestException as error:
        error_text = f"Ошибка при запросе: {error}."
        logger.error(error_text)
        raise ValueError(error_text)
    logger.info("Функция send_request выполнена.")
    # return None


def start(update: Update, context: CallbackContext) -> None:
    """Отвечает пользователю на команду /start."""
    update.message.reply_text(MESSAGES["start"])
    update.message.reply_text(MESSAGES["new_search"])
    logger.debug("Бот запущен")


def alert_message(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(TECH_MESSAGES["alert_message"])
    logger.info("Пользователь ввел картинку или аудио")


def get_message(update: Update, context: CallbackContext) -> None:
    """Основная логика работы бота тут.
    Отвечает пользователю на запросы о проверки названия.
    Инициирует отправку запроса к API и валидацию этого запроса.
    Также инициирует сбор информации о пользователе и
    отправку данных о нем в CRM.
    """
    global TM_NAME
    try:
        TM_NAME = update.message.text
        if check_message(TM_NAME):
            update.message.reply_text(
                MESSAGES["check_title_1"] + TM_NAME + "\n" + (
                    MESSAGES["check_title_2"]))
            logger.debug(
                f"Пользователь ввел название -> {TM_NAME} <- для проверки")
        else:
            update.message.reply_text(TECH_MESSAGES["tm_name_error"])
            logger.debug(f"Название: {TM_NAME} не подходит для проверки.")

        data_string = "type=generate&data[queryText]=" + TM_NAME + "&sync=true"
        response = send_request(
            url=API_ENDPOINT,
            headers=API_HEADERS,
            data=data_string.encode("utf-8"))
        # data=data_string.encode("utf-8")
        logger.info(f"К API отправлен запрос: {TM_NAME}.")

        if check_response(response):
            answer_text = create_answer(response)
            update.message.reply_text(answer_text)
            logger.info("Пользователь получил результаты проверки.")
        else:
            update.message.reply_text(TECH_MESSAGES["api_error"])
            logger.warning("Пользователь не получил результаты проверки.")

        user_general = update.message.from_user
        logger.debug(f"Получена информация о пользователе: {user_general}")
        update.message.reply_text(MESSAGES["new_search"])
        crm_date = create_crm_data(user_general)
        logger.debug(f"Получена crm_date: {crm_date}")
        crm_response = send_request(
            url=CRM_ENDPOINT,
            headers=CRM_HEADERS,
            data=json.dumps(crm_date))
        logger.debug(f"В CRM отправлен json с данными: {crm_date}.")
        logger.info(f"В CRM получили результаты: {crm_response}.")
        logger.debug("В CRM спят.")

    except Exception as error:
        logger.error(f"Ошибка в функции get_message(): {error}")
        update.message.reply_text(TECH_MESSAGES["bot_error"])

    finally:
        logger.info("Функция get_message выполнена.")


def main() -> None:
    """Запускает бота."""
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher
    handlers = [
        CommandHandler("start", start),
        CommandHandler("restart", start),
        MessageHandler(Filters.text & ~Filters.command, get_message),
        MessageHandler(
            (Filters.audio | Filters.photo) & ~Filters.command, alert_message
        )
    ]
    for handler in handlers:
        dispatcher.add_handler(handler)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

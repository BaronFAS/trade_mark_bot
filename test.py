import os
import sys
import logging
import telegram
import requests
import re

from typing import List, Dict, Union
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv
from http import HTTPStatus


load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_ENDPOINT = os.getenv("API_ENDPOINT")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
HEADERS = {
    "Content-Type": f"{os.getenv('CONTENT_TYPE')}",
    "X-Requested-With": f"{os.getenv('X_REQUESTED_WITH')}",
    "Authorization": f"{os.getenv('AUTHORIZATION')}",
}
TM_NAME = None
"""Хранит название которые пользователь ввел для проверки."""
# Может стоит сделать списком и хранить историю проверок?
MESSAGES = {
    "start": "Привет, я @search_trade_mark_bot 🚀\n\n🔎 Бесплатно проверяю название на возможность регистрации по базе Роспатента",
    "new_search": "🚀 Введите название, которое вы хотели бы проверить",
    "check_title_1": "Принял 👌 Проверяю название: ",
    "check_title_2": "Подключаюсь к базе Роспатента.\nВ течение минуты пришлю результат проверки и ссылку на детальный отчет.",
}
TECH_MESSAGES = {
    "help": "Вам нужна помощь? Вот как пользоваться ботом.",
    "как дела?": "У меня все хорошо, спасибо. А у вас?",
    "wrong_input": "Извините, я не понимаю ваш запрос. Попробуйте еще раз или нажмите кнопку help.",
    "tm_name_error": "Извините, такое название неподходит, введите слово или несколько слов на русском языке или латиницей",
    "api_error": "Извините произошла ошибка, попробуйте позднее"
}
RESULTS_CHECK = {
    "High": "😔 Найдены очень похожие товарные знаки.\n\n🛑 Вероятность регистрации низкая.\n\n📑 Подробный отчет о схожих товарных знаках можно посмотреть по ссылке: ",
    "Medium": "🤔 Найдены похожие товарные знаки.\n\n🟡 Вероятность регистрации средняя.\n\n📑 Подробный отчет о схожих товарных знаках можно посмотреть по ссылке: ",
    "Low": "🥳 Поздравляем, ваше название уникально!\n\n🟢 Вероятность регистрации высокая.",
    "None": "🥳 Поздравляем, ваше название уникально!\n\n🟢 Вероятность регистрации высокая.",
    "false": "Ошибка",
}

BOT = telegram.Bot(token=TELEGRAM_TOKEN)
"""Создаем экземпляр бота."""

logging.basicConfig(
    level=logging.DEBUG,
    filename="log_bot",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
"""Логируем бота."""
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)


# def send_request_crm(user):
#     pass


def check_response(response: Dict[str, Union[int, str, bool]]) -> bool:
    global RESULTS_CHECK
    print(response["id"])
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
    logger.debug("Полученный json от API правильный")
    return True


def create_answer(response: List[str]) -> str:
    url_for_analytics = response["urlCheck"] + "?full=true&utmSource=telegram"
    global RESULTS_CHECK
    match response["resultCheck"]:
        case "High":
            answer = RESULTS_CHECK["High"] + url_for_analytics
            logger.debug("Результаты проверки по Higt")
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
            logger.warning("Ошибка в реузльтатах проверки")
            answer = TECH_MESSAGES["api_error"]
    return answer


def check_message(input_data: str) -> bool:
    if re.fullmatch(r'^[\w\d_\-=.,]{1,100}$', input_data):
        logger.debug("Запрос, соответствует параметрам.")
        return True
    return False


def send_request_to_api_web(input_data: str) -> List[str]:
    """Посылает пост запрос и получает ответ от api."""
    data = "type=generate&data[queryText]=" + input_data + "&sync=true"
    try:
        response = requests.post(
            url=API_ENDPOINT, headers=HEADERS, data=data.encode("utf-8")
        )
        logger.debug(f"К API отправлен запрос: {input_data}.")

    except Exception as error:
        error_text = f"Ошибка при запросе к API: {error}."
        logger.error(error_text)
        raise ValueError(error_text)

    finally:
        logger.info("Функция send_request_to_api_web выполнена.")
    if response.status_code != HTTPStatus.OK:
        error_text = f"Ошибочный ответ от API: {response.status_code}"
        logger.error(error_text)
        raise ValueError(error_text)

    logger.debug(f"От API получен ответ: {response.json()}.")
    return response.json()


def start(update, context):
    """Отвечает пользователю на команду /start."""
    update.message.reply_text(MESSAGES["start"])
    update.message.reply_text(MESSAGES["new_search"])
    logger.debug("Бот запущен")


def get_message(update, context):
    """ Основная логика работы бота тут.
    Отвечает пользователю на запросы о проверки названия.
    Инициирует отправку запроса к API его валидацию.
    А так же инициирует сбор информации о пользователе и
    отправку данных о нем в CRM.
    """
    global TM_NAME
    TM_NAME = update.message.text
    if check_message(TM_NAME):
        update.message.reply_text(
            MESSAGES["check_title_1"] + TM_NAME + "\n" + MESSAGES["check_title_2"]
        )
        logger.debug(f"Пользователь ввел название: {TM_NAME} для проверки")
    else:
        update.message.reply_text(TECH_MESSAGES["tm_name_error"])
        logger.debug(f"Название: {TM_NAME} не подходит для проверки")
        return
    response = send_request_to_api_web(TM_NAME)
    if check_response(response):
        answer_text = create_answer(response)
        update.message.reply_text(answer_text)
        logger.debug("Пользователь получил результаты проверки")
    else:
        update.message.reply_text(TECH_MESSAGES["api_error"])
        logger.warning("Пользователь не получил результаты проверки")
    user_general = update.message.from_user
    logger.debug(f"Общая информация о пользователе {user_general}")
    # user_id = user_general["id"]
    # user = BOT.get_user(user_id)
    # logger.debug(f"Детальная нформация о пользователе {user}")
    # send_request_crm(user_general)
    update.message.reply_text(MESSAGES["new_search"])


def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    """Создаем объект Updater и передаем ему токен бота."""
    dispatcher = updater.dispatcher
    """Получаем объект диспетчера для регистрации обработчиков."""
    dispatcher.add_handler(CommandHandler("start", start))
    """Регистрируем обработчик команды /start."""
    dispatcher.add_handler(
        MessageHandler(Filters.text & ~Filters.command, get_message)
    )
    """Регистрируем обработчик сообщений."""
    # Сюда надо добавить обрабочик картинок и аудио, что бы упросить валидацию.
    updater.start_polling()
    """Запускаем бота."""


if __name__ == "__main__":
    main()

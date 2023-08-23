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


def check_response(response: Dict[str, Union[int, str, bool]]) -> bool:
    if not response["id"].isdigit():
        logger.warning("Ошибка API, ID должен быть int")
        return
    # ПРОДОЛЖИТЬ


def create_answer(response: List[str]) -> str:
    pass


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
    """Отвечает пользователю на запросы о проверки названия."""
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

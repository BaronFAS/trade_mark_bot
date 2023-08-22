import os
import logging
import re
import sys
import telegram
import requests
from http import HTTPStatus
from typing import List
from dotenv import load_dotenv
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          CallbackQueryHandler)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
API_ENDPOINT = os.getenv('API_ENDPOINT')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
HEADERS = {
    "Content-Type": f"{os.getenv('CONTENT_TYPE')}",
    "X-Requested-With": f"{os.getenv('X_REQUESTED_WITH')}",
    "Authorization": f"{os.getenv('AUTHORIZATION')}"
}
MESSAGES = {
    'start': 'Привет, я @search_trade_mark_bot 🚀',
    'new_search': '🚀 Введите название, которое вы хотели бы проверить',
    'help': 'Вам нужна помощь? Вот как пользоваться ботом.',
    'как дела?': 'У меня все хорошо, спасибо. А у вас?',
    'wrong_input': 'Извините, я не понимаю ваш запрос. Попробуйте еще раз или нажмите кнопку help.'
}
BUTTONS = {
    'start': 'Начать переписку'
}
RESULTS_CHECK = {
    'High': 'высокая',
    'Low': 'низкая'
}
# Логи
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

# Создаем экземпляр бота
bot = telegram.Bot(token=TELEGRAM_TOKEN)


# Функция для обработки команды /start
def start(update, context):
    keyboard = [[InlineKeyboardButton(
        BUTTONS['start'],
        callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=MESSAGES['start'],
        reply_markup=reply_markup
    )


def send_request_to_api_web(input_data: str) -> List[str]:
    """Посылает пост запрос и получает ответ от api."""
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
    # print(response.json())
    return response.json()


# Функция для обработки текстовых сообщений от пользователя
def handle_message(update, context):
    # Получаем текст сообщения от пользователя
    message_text = update.message.text.lower()
    logger.debug(f'От Пользователя получено сообщение: {message_text}.')
    # Обрабатываем запрос и получаем ответ
    if message_text in MESSAGES:
        response_text = MESSAGES[message_text]

    elif (message_text not in MESSAGES and
          re.match(r'[\w\d_\-=.]{1,30}', message_text)):
        logger.debug(
            'Пользователь направил запрос, соответствующий параметрам.')
        raw_response = send_request_to_api_web(message_text)
        complexity = RESULTS_CHECK[raw_response['resultCheck']]
        url_report = raw_response['urlCheck']
        logger.debug(
            f'Вычислена вероятность регистрации названия: {complexity}.')
        logger.debug(
            f'Сгенерирована ссылка на полный отчет: {url_report}.')

        response_text = (
            f'Ваш запрос обработан. Вероятность регистрации названия: {complexity}. '
            f'Чтобы получить полный отчет, перейдите по ссылке: {url_report}')

    else:
        response_text = MESSAGES['wrong_input']

    # Отправляем ответ пользователю
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=response_text)


def button(update, context):
    query = update.callback_query
    query.answer()
    query.edit_message_text(
        text=('Введите название, которое вы хотели бы проверить.'
              'Вы получите ответ в течение минуты.')
    )


# Добавляем обработчик кнопки при первом входе в чат с ботом
def send_start_button(context):
    keyboard = [[InlineKeyboardButton(
        BUTTONS['start'],
        callback_data='start')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=MESSAGES['start'],
        reply_markup=reply_markup
    )


# Создаем экземпляр Updater и добавляем обработчики команд и сообщений
updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
dispatcher = updater.dispatcher
# Добавляем обработчик команды /start
dispatcher.add_handler(CommandHandler('start', start))
# Добавляем обработчик сообщений от пользователя
dispatcher.add_handler(MessageHandler(
    Filters.text & ~Filters.command, handle_message))
dispatcher.run_async(send_start_button, context=updater)
# Добавляем обработчик callback-кнопки
dispatcher.add_handler(CallbackQueryHandler(button))

# Запускаем бота
updater.start_polling()

# Логгируем бота.
import sys
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Создание обработчика для вывода в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(message)s")
console_handler.setFormatter(console_formatter)

logger.addHandler(console_handler)


# Создание обработчика для записи в файл
file_handler = logging.FileHandler(
    filename="log_bot",
    mode="w",
    encoding="utf-8")

file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s")
file_handler.setFormatter(file_formatter)

logger.addHandler(file_handler)

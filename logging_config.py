# Логгируем бота.
import sys
import logging


logging.basicConfig(
    level=logging.DEBUG,
    filename="log_bot",
    filemode="w",
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

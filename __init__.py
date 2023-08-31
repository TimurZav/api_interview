import os
from logging import Formatter, getLogger, INFO
from logging.handlers import RotatingFileHandler


LOG_FORMAT: str = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
DATE_FTM: str = "%d.%m.%Y %H:%M"
MAX_FILE_SIZE: int = 1024 * 1024  # 1 МБ
MAX_FILES: int = 3

DICT_URLS: dict = {
    "users": "https://json.medrocket.ru/users",
    "tasks": "https://json.medrocket.ru/todos"
}


def get_file_handler(name: str) -> RotatingFileHandler:
    log_dir_name: str = "logging"
    if not os.path.exists(log_dir_name):
        os.mkdir(log_dir_name)
    file_handler: RotatingFileHandler = RotatingFileHandler(
        f"{log_dir_name}/{name}.log",
        maxBytes=MAX_FILE_SIZE,
        backupCount=MAX_FILES
    )
    file_handler.setFormatter(Formatter(LOG_FORMAT, datefmt=DATE_FTM))
    return file_handler


def get_logger(name: str) -> getLogger:
    logger: getLogger = getLogger(name)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(get_file_handler(name))
    logger.setLevel(INFO)
    return logger
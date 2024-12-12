import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# Створюємо папку для логів якщо її немає
LOG_FOLDER = 'logs'
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

# Налаштування логера
def setup_logger():
    logger = logging.getLogger('file_server')
    logger.setLevel(logging.INFO)

    # Формат логування
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )

    # Налаштування ротації логів (максимум 10MB, зберігаємо 5 файлів)
    log_file = os.path.join(LOG_FOLDER, 'file_server.log')
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger 
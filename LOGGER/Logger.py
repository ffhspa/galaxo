import os
import logging
from datetime import datetime
from GALAXO.CONFIG.Version import Version

class Logger:
    def __init__(self, log_path, log_filename, log_level):
        os.makedirs(log_path, exist_ok=True)
        log_file = os.path.join(log_path, log_filename)

        # Datei umbenennen, wenn größer als 5MB
        if os.path.isfile(log_file) and os.path.getsize(log_file) > 5 * 1024 * 1024:
            date_str = datetime.now().strftime('%Y-%m-%d')
            new_log_file = os.path.join(log_path, f"{date_str}_{log_filename}")
            os.rename(log_file, new_log_file)

        logger = logging.getLogger()
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d  - %(message)s'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        logger.info(f"Application started with Version: {Version}")

    def get_logger(self):
        return logging.getLogger()

import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_file):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    warning_logger = logging.getLogger('warnings')
    warning_logger.setLevel(logging.WARNING)
    warning_logger.addHandler(handler)

    return logger, warning_logger

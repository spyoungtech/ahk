import os
import logging

def make_logger(name):
    logger = logging.getLogger(name)
    handler = logging.NullHandler()
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    if os.environ.get('AHK_DEBUG'):
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.ERROR)
    return logger

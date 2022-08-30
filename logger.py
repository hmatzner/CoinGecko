import logging
import sys


def logger():
    """
    Performs the logging of a file given
    @param name: name of the log file
    @return: logger object
    """
    NAME = 'coingecko'

    logger = logging.getLogger(NAME)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s'
        '-LINE:%(lineno)d-%(message)s')

    file_handler = logging.FileHandler(NAME + '.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.ERROR)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger



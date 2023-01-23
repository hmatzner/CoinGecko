import logging
import sys


def logger(name):
    """
    Performs the logging of a file given
    @param name: name of the log file
    @return: logger object
    """

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s'
        '-LINE:%(lineno)d-%(message)s')

    file_handler = logging.FileHandler(name + '.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # stream_handler = logging.StreamHandler(stream=None)
    # stream_handler.setLevel(logging.ERROR)
    # stream_handler.setFormatter(formatter)
    # logger.addHandler(stream_handler)

    return logger



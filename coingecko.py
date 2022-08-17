import webscraper
from database import Database
import API
import logging
import sys


def set_logger(name):
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

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.ERROR)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    return logger


def main():
    """
    Main function of the module that calls the web scraper, API and database files
    """
    Database(*webscraper.main(), logger=set_logger('database'))
    print(API.main(logger_input=set_logger('API')))


if __name__ == '__main__':
    main()

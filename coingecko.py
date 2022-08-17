import webscraper
from database_object2 import Database
import API
import logging
import sys


def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        '%(asctime)s-%(levelname)s-FILE:%(filename)s-FUNC:%(funcName)s-LINE:%(lineno)d-%(message)s')

    file_handler = logging.FileHandler(name+'.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.ERROR)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    
    return logger


def main():
    # df_coins, df_historical, df_wallets, df_distinct_wallets = webscraper.main()
    # Database(*webscraper.main(), logger=set_logger('database'))
    print(API.main(logger_input=set_logger('API')))


if __name__ == '__main__':
    main()

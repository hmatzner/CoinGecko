import sys
from os.path import exists
import logging
import argparse
import re
from datetime import datetime
import webscraper
import API
from database import Database


MIN_NUMBER_OF_COINS = 1
MAX_NUMBER_OF_COINS = 100


def argument_parser():
    parser = argparse.ArgumentParser(description="Useful information: 'd' and 'D' are mutually exclusive and \
    only one of them is expected at most.")
    parser.add_argument('-f', '--from_coin', type=int, metavar='', help='Input from which coin (1 to 100), \
    you would like to receive information about. Default value: f=1.')
    parser.add_argument('-t', '--to_coin', type=int, metavar='', help='Input until which coin (1 to 100), \
    you would like to receive information about. Default value: t=100.')

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--days', type=int, metavar='', help='Input number of days of historical \
    data you want to see (default: maximum available for each coin).')
    group.add_argument('-D', '--date', type=str, metavar='', help='Input from which date you want to see \
    the historical data (format: YYYY-MM-DD, default: maximum available for each coin).')

    args = parser.parse_args()

    return args


def argument_format_checker(args):
    f = args.from_coin
    t = args.to_coin
    days = args.days
    date = args.date

    if f is None:
        f = MIN_NUMBER_OF_COINS
    if f not in range(1, MAX_NUMBER_OF_COINS + 1):
        print("ERROR: The value of the argument 'from_coin' must be an integer from 1 to 100.")
        # sys.exit(1)
        return
    f -= 1

    if t is None:
        t = MAX_NUMBER_OF_COINS
    if t not in range(1, MAX_NUMBER_OF_COINS + 1):
        print("ERROR: The value of the argument 'to_coin' must be an integer from 1 to 100.")
        # sys.exit(1)
        return

    if date is not None:
        date_correct = re.search('^\\d{4}-\\d{2}-\\d{2}$', date)
        if date_correct is None:
            print("ERROR: The format of the argument 'date' should be YYYY-MM-DD.")
            # sys.exit(1)
            return
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print("ERROR: The argument 'date' is invalid.")
            # sys.exit(1)
            return

    if days is not None and days < 0:
        print("ERROR: The argument 'days' should be a non-negative integer.")
        # sys.exit(1)
        return

    return f, t, days, date


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
    # TODO
    """
    logger = set_logger('coingecko')

    args_parser = argument_parser()

    args = argument_format_checker(args_parser)
    if args is None:
        return
    else:
        f, t, days, date = args


    scraper_results = webscraper.dataframes_creator(f, t, days, date)

    coins = scraper_results['coins']['coin_name'].to_list()
    print(coins)

    # coins = ['Bitcoin', 'Ethereum', 'Tether', 'USD Coin']

    # matching names returned from web scraper to those database receive
    # keys_matcher = {'coins': 'coins', 'hist': 'hist', 'wallets': 'wallets', 'wallets_names': 'wallets_names'}
    # TODO: remove the keys_matcher and make the column names match from the beginning
    #
    # database_args = {keys_matcher[k]: v for k, v in scraper_results.items()}
    # print(f'Database_args = {database_args}')

    if exists("configurations.json"):
        db = Database(init=False, logger=set_logger('database'))
        db.update_all(scraper_results)
        db.close_connection()

    else:
        print("configurations.json should be created. for format of file look at README.md")
        logger.error("configurations.json should be created")

    # api_results = API.main(coins=coins, logger_input=set_logger('API'))
    # print(pd.DataFrame(api_results))
    # print("Data obtained from the API with coin and price in USD:")
    #
    # for coin, val in api_results.items():
    #     print(coin.title(), val)
    #



if __name__ == '__main__':
    main()

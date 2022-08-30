from os.path import exists
import argparse
import re
from datetime import datetime
from webscraper import dataframes_creator
import API
from database import Database
from logger import logger
import time

logger = logger('coingecko')


def argument_parser():
    parser = argparse.ArgumentParser(description="Useful information: 'd' and 'D' are mutually exclusive and \
    only one of them is expected at most.")
    parser.add_argument('-f', '--from_coin', type=int, metavar='', help='Input from which coin (1 to 100), \
    you would like to receive information about. Default value: f=1.')
    parser.add_argument('-t', '--to_coin', type=int, metavar='', help='Input until which coin (1 to 100), \
    you would like to receive information about. Default value: t=100.')

    parser.add_argument('--init_tables', action='store_true', help='If True: tables will be created from scratch. \
    Default value: False.')
    parser.set_defaults(init_tables=False)

    parser.add_argument('--print_coins', action='store_true', help='If True: prints the coins table from SQL server. \
        Default value: False.')
    parser.set_defaults(print_coins=False)

    group = parser.add_mutually_exclusive_group()
    group.add_argument('-d', '--days', type=int, metavar='', help='Input number of days of historical \
    data you want to see (default: maximum available for each coin).')
    group.add_argument('-D', '--date', type=str, metavar='', help='Input from which date you want to see \
    the historical data (format: YYYY-MM-DD, default: maximum available for each coin).')

    args = parser.parse_args()

    return args


def arguments_format_checker(args):
    MIN_COINS = 1
    MAX_COINS = 100
    f = args.from_coin
    t = args.to_coin
    init_tables = args.init_tables
    print_coins = args.print_coins
    days = args.days
    date = args.date

    if f is None:
        f = MIN_COINS
    if f not in range(1, MAX_COINS + 1):
        logger.error("ERROR: The value of the argument 'from_coin' must be an integer from 1 to 100.")
        return
    f -= 1

    if t is None:
        t = MAX_COINS
    if t not in range(1, MAX_COINS + 1):
        logger.error("ERROR: The value of the argument 'to_coin' must be an integer from 1 to 100.")
        return

    if date is not None:
        date_correct = re.search('^\\d{4}-\\d{2}-\\d{2}$', date)
        if date_correct is None:
            logger.error("ERROR: The format of the argument 'date' should be YYYY-MM-DD.")
            return
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            logger.error("ERROR: The argument 'date' is invalid.")
            return

    if days is not None and days < 0:
        print("ERROR: The argument 'days' should be a non-negative integer.")
        return

    return f, t, init_tables, print_coins, days, date


def main():
    """
    # TODO
    """

    args_parser = argument_parser()

    args = arguments_format_checker(args_parser)
    if args is None:
        return
    else:
        f, t, init_tables, print_coins, days, date = args

    start = time.perf_counter()
    scraper_results = dataframes_creator(f, t, days, date)
    print(f'Time taken to get the data from the web scraper: {(time.perf_counter() - start):.2f} seconds.\n')

    if exists("configurations.json"):
        start = time.perf_counter()

        db = Database(init=init_tables)
        if init_tables:
            db.update_all(scraper_results)
        else:
            db.update_coins(scraper_results['coins'])

        if print_coins:
            db.show_coins()
        db.close_connection()

        print(f'Time taken to store data in SQL: {time.perf_counter() - start:.2f} seconds.\n')

    else:
        logger.error("ERROR: The file configurations.json does not exist.")

    coins = scraper_results['coins']['coin_name'].to_list()

    start = time.perf_counter()
    api_results = API.main(coins=coins)
    print(f'Time taken to get the data from the API: {(time.perf_counter() - start):.2f} seconds.\n')
    print(api_results)


if __name__ == '__main__':
    main()

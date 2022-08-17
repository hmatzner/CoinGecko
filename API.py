import requests
import time
from datetime import datetime


api_url = "https://api.coingecko.com/api/v3/coins/"


def get_json(url_path, params=None):
    """
    Performs a request to get a JSON file
    @param url_path: URL path
    @param params: parameters for the request
    @return: a JSON file of its content
    """
    resp = requests.get(url=api_url + url_path, params=params)
    return resp.json()


BIT_TO_USD = get_json('usd-coin')['market_data']['current_price']['btc']


def get_coin_current_price(json_coin):
    """
    Searches for a coin's price
    @param json_coin: JSON file of a coin
    @return: a coin's current price in USD
    """
    try:
        return json_coin['market_data']['current_price']['btc']/BIT_TO_USD
    except Exception as e:
        logger.error(e)


def get_coin_market_cap(json_coin):
    """
    Searches for a coin's market cap
    @param json_coin: JSON file of a coin
    @return: a coin's current market cap in USD
    """
    try:
        return json_coin['market_data']['market_cap']['btc']/BIT_TO_USD
    except Exception as e:
        logger.error(e)


def get_historical(coin_id, days, *, vs_currency='usd', interval='daily'):
    """
    @param coin_id: coin unique name, e.g. 'bitcoin' for bitcoin
    @param days: number of days from today to get historcal data
    @param vs_currency: should
    """
    try:
        params = dict(days=days, vs_currency=vs_currency, interval=interval)
        suffix = coin_id + '/market_chart'
        return fix_time_stamps(get_json(suffix, params))
    except Exception as e:
        logger.error(e)


def fix_time_stamps(history_json):
    """
    A helper function for get_historical
    Fixes timestamps to human time
    """
    # print(f"(fix_time_stamps)historical:\n{history_json}")
    try:
        fixed_history = dict()
        for k, lst in history_json.items():
            fixed_history[k] = [[datetime.fromtimestamp(sub_list[0]//1000).strftime("%d/%m/%Y"), sub_list[1]] for sub_list in lst]
        return fixed_history
    except Exception as e:
        logger.error(e)


def main(coins=None, days=10, logger_input=None):
    start = time.perf_counter()
    global logger
    logger = logger_input
    logger.info("in")
    dict_ = dict()
    try:
        if coins:
            coins = [coin.lower() for coin in coins]
            for coin in coins:
                data = get_json(coin)
                dict_[coin] = get_coin_current_price(data)
    except Exception as e:
        logger.error(e)

    try:
        if days:
            print(f"last {days} days:")
            print(f"Historical data of the last {days} days:")
            if coins:
                coin = coins[0]
            else:
                coin = 'bitcoin'


            historical = get_historical(coin, days)
            print(f"historical: \n{historical}")
    except Exception as e:
        logger.error(e)

    end = time.perf_counter()
    print(f'Time taken to get the data from the API: {(end - start):.2f} seconds.\n')
    return dict_

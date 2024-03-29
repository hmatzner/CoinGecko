import requests
from datetime import datetime
from logger import logger
import pandas as pd

logger = logger('API')
API_URL = "https://api.coingecko.com/api/v3/coins/"


def get_json(url_path, params=None):
    """
    Performs a request to get a JSON file
    @param url_path: URL path
    @param params: parameters for the request
    @return: a JSON file of its content
    """
    resp = requests.get(url=API_URL + url_path, params=params)
    return resp.json()


BIT_TO_USD = get_json('usd-coin')['market_data']['current_price']['btc']


def get_coin_current_price(json_coin):
    """
    Searches for a coin's price
    @param json_coin: JSON file of a coin
    @return: a coin's current price in USD
    """
    # try:
    return json_coin['market_data']['current_price']['btc']/BIT_TO_USD
    # except Exception as e:
    #     logger.error(e)


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
    @param coin_id: coin name, e.g. 'bitcoin' for bitcoin
    @param days: number of days from today to get historical data
    @param vs_currency: string of currency alias
    @param interval: periodicity of row's information
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
    try:
        fixed_history = dict()
        for k, lst in history_json.items():
            if type(lst) == str:
                continue
            fixed_history[k] = [[datetime.fromtimestamp(int(sub_list[0]) // 1000).strftime("%d/%m/%Y"), sub_list[1]] for sub_list in lst]
        return fixed_history
    except Exception as e:
        logger.error(e)


def main(coins=None, days=10):
    """

    @param coins:
    @param days:
    @return:
    """
    # start = time.perf_counter()
    logger.info("in")
    coins_df = dict()

    if coins:
        coins = [coin.lower().replace(' ', '-') for coin in coins]
        for coin in coins:
            try:
                data = get_json(coin)
                coins_df[coin] = get_coin_current_price(data)
            except Exception as e:
                logger.error(e)

    historical = dict()
    if days:
        for coin in coins:
            try:
                historical[coin] = get_historical(coin, days)
            except Exception as e:
                logger.error(e)

    # print(f"Historical data of the last {days} days:")
    # print(historical)
    return pd.Series(coins_df, name='coins')

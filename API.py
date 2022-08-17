import requests


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
    return json_coin['market_data']['current_price']['btc']/BIT_TO_USD


def get_coin_market_cap(json_coin):
    """
    Searches for a coin's market cap
    @param json_coin: JSON file of a coin
    @return: a coin's current market cap in USD
    """
    return json_coin['market_data']['market_cap']['btc']/BIT_TO_USD


def get_historical(coin_id, days, vs_currency='usd', interval='daily'):
    params = dict(days=days, vs_currency=vs_currency, interval=interval)
    suffix = coin_id + '/market_chart'
    return get_json(suffix, params)


def main(logger_input=None):
    global logger
    logger = logger_input
    logger.info("in")
    btc_json = get_json('bitcoin')
    eth_json = get_json('ethereum')
    print(f"Bitcoin value: USD {get_coin_current_price(btc_json)}")
    print(f"Ethereum value: USD {get_coin_current_price(eth_json)}")
    print(f"\nHistory of last 2 days of Bitcoin:\n{get_historical('Bitcoin', 2)}")
    # return btc_json, eth_json


# Example
# print("example")
# btc_json = get_json('bitcoin')
# eth_json = get_json('ethereum')
# print(f"bitcoin value: {get_coin_current_price(btc_json)}$")
# print(f"ethereum value: {get_coin_current_price(eth_json)}$")
# print(f"\nhistory of last 2 days of bitcoin:\n{get_historical('bitcoin', 2)}")

import requests

api_url = "https://api.coingecko.com/api/v3/coins/"


def get_json(url_suffix, params=None):
    """recieves a url of some API address
       returns a json file of its content
       """
    resp = requests.get(url=api_url+url_suffix, params=params)
    return resp.json()


BIT_TO_USD = get_json('usd-coin')['market_data']['current_price']['btc']


def get_coin_current_price(json_coin):
    """recieves a json file of a coin and returns its current price in USD"""
    return json_coin['market_data']['current_price']['btc']/BIT_TO_USD


def get_coin_market_cap(json_coin):
    """recieves a json file of a coin and returns its market_cap in USD"""
    return json_coin['market_data']['market_cap']['btc']/BIT_TO_USD


def get_historical(coin_id, days, vs_currency='usd', interval='daily'):
    params = dict(days=days, vs_currency=vs_currency, interval=interval)
    suffix = coin_id + '/market_chart'
    return get_json(suffix, params)



#example
print("example")
btc_json = get_json('bitcoin')
eth_json = get_json('ethereum')
print(f"bitcoin value: {get_coin_current_price(btc_json)}$")
print(f"ethereum value: {get_coin_current_price(eth_json)}$")
print(f"\nhistory of last 2 days of bitcoin:\n{get_historical('bitcoin', 2)}")
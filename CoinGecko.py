import requests
import grequests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd

BATCH_SIZE = 25


def get_soup(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    return soup


def extract_price_and_market_cap(dom):
    for i in (4, 5, 6):
        try:
            price = dom.xpath(f'/html/body/div[5]/div[{i}]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text
            market_cap = dom.xpath(f'/html/body/div[5]/div[{i}]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text
            return price, market_cap
        except:
            continue
        
        
def use_requests(soup):
    """
    builds a dataframe of form {coin: price, market_cap, url}
    uses the requests library
    """
    scraped_coins = soup.find_all('a', class_= "tw-hidden lg:tw-flex font-bold tw-items-center tw-justify-between")
    dict1 = {} #{coin_name: [price, market_cap, url]}

    for coin in scraped_coins:
        coin_name = coin.text.strip()
        coin_url = 'https://www.coingecko.com' + coin['href']
        soup_coin = get_soup(coin_url)
        dom = etree.HTML(str(soup_coin))
        price, market_cap = extract_price_and_market_cap(dom)
        dict1[coin_name] = (price, market_cap, coin_url)
        
    df = pd.DataFrame.from_dict(dict1, orient='index', columns=('price', 'market cap', 'url'))
    print (df.drop(columns=['url']))
    if df.isna().to_numpy().sum() != 0:
        print("some values are missing")
    return df


def use_grequests(soup):
    """
    builds a dataframe of form {coin: price, market_cap, url}
    uses the grequests library
    
    !currently not working!
    
    """
    scraped_coins = soup.find_all('a', class_= "tw-hidden lg:tw-flex font-bold tw-items-center tw-justify-between")
    dict1 = {} #{coin_name: [price, market_cap, url]}
    urls = ['https://www.coingecko.com' + coin['href'] for coin in scraped_coins]
    names = [coin.text.strip() for coin in scraped_coins]
    
    rs = (grequests.get(u) for u in urls)
    t = grequests.map(rs, size=BATCH_SIZE)
    
    for idx, item in enumerate(t):
        soup_coin = BeautifulSoup(item.text, 'lxml')
        coin_name = names[idx]
        coin_url = urls[idx]
        dom = etree.HTML(str(soup_coin))
        
        price, market_cap = extract_price_and_market_cap(dom)

        # print(f"Currency #{i}: {coin_name}\n"
        #       f"Price: {price}\n"
        #       f"URL: {coin_url}\n"
        #       f"Market Cap: {market_cap}\n")

        dict1[coin_name] = [price, market_cap, coin_url]
    df = pd.DataFrame.from_dict(dict1, orient='index', columns=('price', 'market cap', 'url'))
    return df


def main():
    soup = get_soup('https://www.coingecko.com/')
    df = use_requests(soup)
    # df = use_grequests(soup)
    

if __name__ == '__main__':
    main()

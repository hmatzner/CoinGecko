import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd


def get_soup(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')

    return soup


def all_the_rest(soup):
    scraped_coins = soup.find_all('a', class_= "tw-hidden lg:tw-flex font-bold tw-items-center tw-justify-between")
    coins = list()
    df = pd.DataFrame(columns = ['price', 'market cap'])

    for i, coin in enumerate(scraped_coins[:5],1):
        coin_name = coin.text.strip()
        last_url = coin_name.replace(' ', '-').lower()
        coins.append(last_url)
        coin_url = 'https://www.coingecko.com/en/coins/' + last_url
        soup_coin = get_soup(coin_url)

        price = soup_coin.find('span', class_ = 'no-wrap').text

        dom = etree.HTML(str(soup_coin))

        try:
            market_cap = dom.xpath('/html/body/div[5]/div[5]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text
        except:
            market_cap = dom.xpath('/html/body/div[5]/div[4]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text
        print(f"Currency #{i}: {coin_name}\n"
              f"Price: {price}\n"
              f"URL: {coin_url}\n"
              f"Market Cap: {market_cap}\n")
        tmp_df = pd.DataFrame(data=[[price, market_cap]], columns=['price', 'market cap'], index=[coin_name])

        df = df.append(tmp_df)


def main():
    soup = get_soup('https://www.coingecko.com/')
    return all_the_rest(soup)
    


if __name__ == '__main__':
    df = main()
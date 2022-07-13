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

    df = pd.DataFrame(columns = ['price', 'market cap'])

    for i, coin in enumerate(scraped_coins, 1):
        coin_name = coin.text.strip()
        last_url = coin['href']
        
        coin_url = 'https://www.coingecko.com' + last_url
        soup_coin = get_soup(coin_url)

        dom = etree.HTML(str(soup_coin))


        def price_market_scraper(index):
            return dom.xpath(f'/html/body/div[5]/div[{index}]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text

        for value in range(2):
            for index in range(4,7):
                try:
                    if value == 0:
                        price = price_market_scraper(index)
                    else:
                        market_cap = price_market_scraper(index)
                    break
                except IndexError:
                    pass

        # pip install -r requirements.txt
        # pip freeze > requirements.txt


        # price = soup_coin.find_all('span', class_='no-wrap')[1].text

        # try:
        #     price = dom.xpath('/html/body/div[5]/div[4]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text
        # except IndexError:
        #     try:
        #         price = dom.xpath('/html/body/div[5]/div[5]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text
        #     except IndexError:
        #         price = dom.xpath('/html/body/div[5]/div[6]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text

        # try:
        #     market_cap = dom.xpath('/html/body/div[5]/div[5]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text
        # except IndexError:
        #     try:
        #         market_cap = dom.xpath('/html/body/div[5]/div[4]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text
        #     except IndexError:
        #         market_cap = dom.xpath('/html/body/div[5]/div[6]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text


        # print(f"Currency #{i}: {coin_name}\n"
        #       f"Price: {price}\n"
        #       f"URL: {coin_url}\n"
        #       f"Market Cap: {market_cap}\n")

        # tmp_df = pd.DataFrame(data=[[coin_name, price, int(int(market_cap.replace(',', '').replace('$', '')) // (10**6))]], columns=['coin', 'price', 'market cap (M)'], index=[i])
        # tmp_df = pd.DataFrame(data=[coin_name, price, market_cap], columns=['coin', 'price', 'market cap'])


        # df = df.append(tmp_df)
        # df = pd.concat(tmp_df, df.loc[:]).reset_index(drop=True)
        print(df)

    return df


def main():
    soup = get_soup('https://www.coingecko.com/')
    print(all_the_rest(soup))
    

if __name__ == '__main__':
    main()

import requests
from bs4 import BeautifulSoup
from lxml import etree


def get_soup(url):
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')

    return soup


def all_the_rest(soup):
    scraped_coins = soup.find_all('a', class_= "tw-hidden lg:tw-flex font-bold tw-items-center tw-justify-between")
    coins = list()

    # scraped_links = soup.find('a', class_="tw-hidden lg:tw-flex font-bold tw-items-center tw-justify-between")
    # # scraped_links = soup.find('a', href='/en/coins/bitcoin').next_sibling
    # print(scraped_links)


    for i, coin in enumerate(scraped_coins[50:], 50):
        coin_name = coin.text.strip()
        last_url = coin['href']
        
        coin_url = 'https://www.coingecko.com' + last_url
        soup_coin = get_soup(coin_url)

        dom = etree.HTML(str(soup_coin))

        # price = soup_coin.find_all('span', class_='no-wrap')[1].text

        try:
            price = dom.xpath('/html/body/div[5]/div[4]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text
        except IndexError:
            try:
                price = dom.xpath('/html/body/div[5]/div[5]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text
            except IndexError:
                price = dom.xpath('/html/body/div[5]/div[6]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text

        try:
            market_cap = dom.xpath('/html/body/div[5]/div[5]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text
        except IndexError:
            try:
                market_cap = dom.xpath('/html/body/div[5]/div[4]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text
            except IndexError:
                market_cap = dom.xpath('/html/body/div[5]/div[6]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text

        print(f"Currency #{i}: {coin_name}\n"
              f"Price: {price}\n"
              f"URL: {coin_url}\n"
              f"Market Cap: {market_cap}\n")


def main():
    soup = get_soup('https://www.coingecko.com/')
    all_the_rest(soup)


if __name__ == '__main__':
    main()
import requests
from bs4 import BeautifulSoup
from lxml import etree
import pandas as pd
from tqdm import tqdm
import argparse

COINGECKO_URL = 'https://www.coingecko.com'

parser = argparse.ArgumentParser(description='Indicate how many coins, from 1 to 100, you would like to see.')
parser.add_argument('-k', '--coins', type=int, metavar='', help='Number of coins')
# parser.add_argument('coins', type=int, metavar='', help='Number of coins')


# parser.add_argument('n1', type=float, metavar='', help='First nº of the calculation')
# parser.add_argument('n2', type=float, metavar='',  help='Second nº of the calculation')

# group = parser.add_mutually_exclusive_group()
# group.add_argument('-w', '--morning', action='store_true', help='Gives a "Good morning" message')
# group.add_argument('-n', '--night', action='store_true', help='Gives a "Good night" message')

args = parser.parse_args()


def get_soup(url):
    """
    Performs the request to the main webpage url.
    @param url: main webpage url
    @return: tuple of same url parameter and Beautiful Soup object created
    """
    r = requests.get(url)
    html = r.text
    soup = BeautifulSoup(html, 'lxml')
    return url, soup


def price_scraper(dom, index):
    """
    Returns the complete XPath of the given coin's price.
    @param dom: etree created with an incomplete XPath
    @param index: possible index to find the price of a coin in the XPath
    """
    return dom.xpath(f'/html/body/div[5]/div[{index}]/div[1]/div/div[1]/div[3]/div/div[1]/span[1]/span')[-1].text


def market_scraper(dom, index):
    """
    Returns the complete XPath of the given coin's market cap.
    @param dom: etree created with an incomplete XPath
    @param index: possible index to find the market cap of a coin in the incomplete XPath
    """
    return dom.xpath(f'/html/body/div[5]/div[{index}]/div[1]/div/div[2]/div[2]/div[1]/div[1]/span[2]/span')[-1].text


def web_scraper(url, soup, k):
    """
    Parses the data and creates a Pandas dataframe with the main information of each coin.
    @param url: main webpage's url
    @param soup: Beautiful Soup object created with the requests module
    @param k: number of coins the user selected to see
    @return: a Pandas dataframe
    """
    scraped_coins = soup.find_all('a', class_= "lg:tw-flex font-bold tw-items-center tw-justify-between")
    list_of_lists = list()
    print('Information being retrieved...')

    for coin in tqdm(scraped_coins[:k], total=k):
        coin_name = coin.text.strip()
        coin_url = url + coin['href']
        soup_coin = get_soup(coin_url)
        dom = etree.HTML(str(soup_coin))
        price, market_cap = 0, 0

        for value in range(2):
            for index in range(4,7):
                try:
                    if value == 0:
                        price = price_scraper(dom, index)
                    else:
                        market_cap = market_scraper(dom, index)
                    break
                except IndexError:
                    pass

        list_of_lists.append([coin_name, price, market_cap, coin_url])

    df = pd.DataFrame(list_of_lists, columns=['Coin', 'Price', 'Market Cap', 'URL'])
    df.index = range(1, len(df) + 1)

    print('\n')
    return df


def main():
    """
    Main function of the module that:
    - assigns the operation to perform to a variable
    - prints a message, if any
    - prints the return value of the math operation to perform
    """
    # function = dict_[args.operation]
    # if args.morning:
    #     print('Good morning!')
    # elif args.night:
    #     print('Good night!')
    # print(function(args.n1, args.n2))
    k = args.coins

    if k is None:
        print('ERROR: Please provide a value for k.')
        return

    if k not in range(1, 101):
        print('ERROR: The value of k must be an integer from 1 to 100.')
        return

    url, soup = get_soup(COINGECKO_URL)
    df = web_scraper(url, soup, k)
    print(df)


if __name__ == '__main__':
    main()
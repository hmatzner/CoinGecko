import os
import requests
import argparse
import pandas as pd
import re
from bs4 import BeautifulSoup
from lxml import etree
import lxml.html
from urllib.request import Request, urlopen
from datetime import datetime
from tqdm import tqdm
from database_object2 import Database


COINGECKO_URL = 'https://www.coingecko.com'
MIN_NUMBER_OF_COINS = 1
MAX_NUMBER_OF_COINS = 100

parser = argparse.ArgumentParser(description="Useful information: 'd' and 'D' are mutually exclusive and \
only one of them is expected at most.")
parser.add_argument('-f', '--from_coin', type=int, metavar='', help='Input from which coin (1 to 100), \
you would like to receive information about. Default value: f=1.')
parser.add_argument('-t', '--to_coin', type=int, metavar='', help='Input until which coin (1 to 100), \
you would like to receive information about. Default value: t=100.')

group = parser.add_mutually_exclusive_group()
group.add_argument('-d', '--days', type=int, metavar='', help='Input number of days of historical \
data you want to see (default: maximum available for each coin).')
group.add_argument('-D', '--date', type=str, metavar='', help='Input from which date you want to see \
the historical data (format: YYYY-MM-DD, default: maximum available for each coin).')

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
    # print(type(soup))
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


def csv_reader(url_historical):
    """
    Performs the request to get the historical data, parses it and reads the csv file from the URL.
    @param url_historical: URL of the historical data of a coin
    @return: a csv file
    """
    r = requests.get(url_historical)
    html = r.text
    soup_historical = BeautifulSoup(html, 'lxml')
    historical_links = soup_historical.find_all('a', class_='dropdown-item')[-1]['href']
    req = Request(COINGECKO_URL + historical_links, headers={'User-Agent': 'Mozilla/5.0'})
    csv_file = urlopen(req).read()
    return csv_file


def create_temp_df(coin_index, csv_file, days, date):
    """
    Creates a csv file of the coin's historical data, creates a temporary dataframe and removes the csv file.
    @param coin_index: index of the coin
    @param csv_file: csv format file of the coin's historical data
    @param days: argument passed by the user, specifies how many days of data to save in the dataframe
    @param date: argument passed by the user, specifies from which date of data to save in the dataframe
    @return: a temporary dataframe
    """
    with open(f'csv_{coin_index}', 'wb') as f:
        f.write(csv_file)

    if days is not None:
        temp_df = pd.read_csv(f'csv_{coin_index}').tail(days)
    elif date is not None:
        today = datetime.today()
        delta = (today - date).days + 1
        temp_df = pd.read_csv(f'csv_{coin_index}').tail(delta)
    else:
        temp_df = pd.read_csv(f'csv_{coin_index}')

    temp_df['coin_id'] = coin_index

    os.remove(f'csv_{coin_index}')

    return temp_df


def wallets_scraper(coin_url, dom):

    html = requests.get(coin_url)
    doc = lxml.html.fromstring(html.content)
    div_wallet = doc.xpath('//div[@class="coin-link-row tw-mb-0"]')[0]
    wallet = div_wallet.xpath('//span[@class="tw-self-start tw-py-1 tw-my-0.5 tw-min-w-3/10 2xl:tw-min-w-1/4 tw-text-gray-500 dark:tw-text-white dark:tw-text-opacity-60 tw-mr-2"]/text()')
    # print(f'Wallet is: {wallet}')
    # print(f'Wallet type is: {type(wallet)}')

    if not wallet:
        return None

    # html = requests.get(coin_url)
    # doc = lxml.html.fromstring(html.content)
    # is_wallet = doc.xpath('//div[@class="coin-link-row tw-mb-0"]')[0]
    # yes_is_wallet = is_wallet.xpath('//span[@class="tw-self-start tw-py-1 tw-my-0.5 tw-min-w-3/10 2xl:tw-min-w-1/4 tw-text-gray-500 dark:tw-text-white dark:tw-text-opacity-60 tw-mr-2"]')
    # # print(yes_is_wallet)
    # wallet = list()
    # for i in yes_is_wallet:
    #     wallet.append(i.xpath('//a[@class="tw-px-2.5 tw-py-1 tw-my-0.5 tw-mr-1 tw-rounded-md tw-text-sm tw-font-medium tw-bg-gray-100 tw-text-gray-800 hover:tw-bg-gray-200 dark:tw-text-white dark:tw-bg-white dark:tw-bg-opacity-10 dark:hover:tw-bg-opacity-20 dark:focus:tw-bg-opacity-20 "]/text()'))
    # print(f'Wallet is: {wallet}')
    # print(f'Wallet type is: {type(wallet)}')

    # span_wallets = list()
    # for i in div_wallet:
    #     span_wallets.append(i.xpath('//span[@class="tw-self-start tw-py-1 tw-my-0.5 tw-min-w-3/10 2xl:tw-min-w-1/4 tw-text-gray-500 dark:tw-text-white dark:tw-text-opacity-60 tw-mr-2"]/text()'))
    # print(f'Wallet is: {span_wallets}')
    # print(f'Wallet type is: {type(span_wallets)}')
    # return

    # while True:
    #     current_item = dom.findtext('a')
    #     print('text found is', current_item)
    #     break

    list_of_w = list()
    for index_xpath in range(4, 6):
        index = 1
        try:
            while True:
                list_of_w.append(dom.xpath(f'/html/body/div[5]/div[4]/div[2]/div[2]/div[{index_xpath}]/div/a[{index}]')[-1].text)
                # print(list_of_w)
                index += 1
        except IndexError:
            # print(f'the index is {index}')
            if index != 1:
                return list_of_w
    try:
        list_of_w.append(dom.xpath(f'/html/body/div[5]/div[5]/div[2]/div[2]/div[5]/div/a')[-1].text)
        return list_of_w
    except IndexError:
        return None


def web_scraper(url, soup, f, t, days, date):
    """
    Parses the data and creates a Pandas dataframe with the main information of each coin.
    Calls functions price_scraper, market_scraper, csv_reader and create_temp_df in the process.
    @param url: main webpage's url
    @param soup: Beautiful Soup object created with the requests module
    @param f: argument passed by the user, specifies from which coin to get info about
    @param t: argument passed by the user, specifies until which coin to get info about
    @param days: argument passed by the user, specifies how many days of data to save in the dataframe
    @param date: argument passed by the user, specifies from which date of data to save in the dataframe
    @return: a Pandas dataframe with relevant info about each coin and another one with their historical data
    """
    scraped_links = soup.find_all('a', class_="tw-flex tw-items-start md:tw-flex-row tw-flex-col")
    list_of_lists = list()
    list_of_wallets = list()
    df_historical = None
    print('Information being retrieved...')

    for coin_index, link in tqdm(enumerate(scraped_links[f: t], 1), total=t-f):
        coin_name = link.findChild().text.strip()
        print(coin_name)
        coin_url = url + link['href']
        soup_coin = get_soup(coin_url)
        # print(f'type of soup coin is {type(soup_coin)}')
        dom = etree.HTML(str(soup_coin))
        # print(f'type of dom is {type(dom)}')

        price, market_cap, wallets_of_each_coin = (None, None, None)

        # We are going to iterate over the price and the market cap.
        for value in range(2):
            # There are three possible xPath for each coin, being each one of them the same
            # except for one of the indexes that could be 4, 5, or 6.
            for index in range(4, 7):
                try:
                    if value == 0:
                        price = price_scraper(dom, index)
                    else:
                        market_cap = market_scraper(dom, index)
                    break
                except IndexError:
                    pass

        list_of_lists.append([coin_name, price, market_cap, coin_url])

        url_historical = coin_url + '/historical_data#panel'

        csv_file = csv_reader(url_historical)

        temp_df = create_temp_df(coin_index, csv_file, days, date)

        # Assuming Bitcoin is the #1 coin. If the flippening was to happen, the code should be revised.
        if coin_name == 'Bitcoin':
            df_historical = temp_df
        else:
            df_historical = pd.concat([df_historical, temp_df])

        wallets_of_each_coin = wallets_scraper(coin_url, dom)

        # if coin_name not in ('eCash', 'Gate', 'PAX Gold', 'Tenset', 'Curve DAO'):
        #     wallets = wallets_scraper(dom)
        #     list_of_wallets.append(wallets)
        list_of_wallets.append([coin_name, wallets_of_each_coin])
        print(list_of_wallets[-1])

        # list_of_lists.append([coin_name, price, market_cap, coin_url])


    # print(list_of_wallets)
    df_wallets = pd.DataFrame(list_of_wallets, columns=['coin_name', 'wallets'])
    df_wallets.index = range(1, len(df_wallets) + 1)
    df_wallets.reset_index(inplace=True)

    df_coins = pd.DataFrame(list_of_lists, columns=['coin_name', 'price', 'market_cap', 'URL'])
    df_coins.index = range(1, len(df_coins) + 1)
    df_coins.reset_index(inplace=True)

    for column in ('price', 'market_cap'):
        df_coins[column] = df_coins[column].str.replace(',', '', regex=False)
        df_coins[column] = df_coins[column].str.replace('$', '', regex=False)
        df_coins[column] = df_coins[column].astype(float)

    df_historical['price'] = df_historical['price'].round(2)
    df_historical.reset_index(drop=True, inplace=True)

    print('\n')
    return df_coins, df_historical, df_wallets


def main():
    """
    Main function of the module:
    - checks all three possible arguments provided by the user have an expected value, giving an error message if needed
    - calls the get_soup and web_scraper functions
    - returns the two dataframes returned by the web_scraped function
    """
    f = args.from_coin
    t = args.to_coin
    days = args.days
    date = args.date

    if f is None:
        f = MIN_NUMBER_OF_COINS
    if f not in range(1, MAX_NUMBER_OF_COINS + 1):
        print("ERROR: The value of the argument 'from_coin' must be an integer from 1 to 100.")
        return
    f -= 1

    if t is None:
        t = MAX_NUMBER_OF_COINS
    if t not in range(1, MAX_NUMBER_OF_COINS + 1):
        print("ERROR: The value of the argument 'to_coin' must be an integer from 1 to 100.")
        return

    if date is not None:
        date_correct = re.search('^\\d{4}-\\d{2}-\\d{2}$', date)
        if date_correct is None:
            print("ERROR: The format of the argument 'date' should be YYYY-MM-DD.")
            return
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            print("ERROR: The argument 'date' is invalid.")
            return

    if days is not None and days < 0:
        print("ERROR: The argument 'days' should be a non-negative integer.")
        return

    url, soup = get_soup(COINGECKO_URL)
    df_coins, df_historical, df_wallets = web_scraper(url, soup, f, t, days, date)

    return df_coins, df_historical, df_wallets
    # return df_coins, df_historical

if __name__ == '__main__':
    print(main())
    # coins, historical_data = main()
    # print(f"within CoinGecko:\n{coins}", end='\n\n')
    # # # Saving to SQL
    # db = Database()
    # db.append_rows_to_coins(coins)
    # db.append_rows_to_history(historical_data)


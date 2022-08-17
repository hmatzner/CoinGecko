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


def create_temp_df(coin_id, csv_file, days, date):
    """
    Creates a csv file of the coin's historical data, creates a temporary dataframe and removes the csv file.
    @param coin_id: index of the coin
    @param csv_file: csv format file of the coin's historical data
    @param days: argument passed by the user, specifies how many days of data to save in the dataframe
    @param date: argument passed by the user, specifies from which date of data to save in the dataframe
    @return: a temporary dataframe
    """
    # Creates a csv file for each coin and writes in it the historical data
    with open(f'csv_{coin_id}', 'wb') as f:
        f.write(csv_file)

    # Uses the parameter either 'days' or 'date' provided (or not) by the user to create a temporary dataframe
    # that reads the csv file created.
    if days is not None:
        temp_df = pd.read_csv(f'csv_{coin_id}').tail(days)
    elif date is not None:
        today = datetime.today()
        delta = (today - date).days + 1
        temp_df = pd.read_csv(f'csv_{coin_id}').tail(delta)
    else:
        temp_df = pd.read_csv(f'csv_{coin_id}')

    temp_df['coin_id'] = coin_id

    # Removes the file created before
    os.remove(f'csv_{coin_id}')

    return temp_df


def wallets_scraper(coin_url, dom):
    """
    Performs a request and gets the wallets of each coin
    @param coin_url: url of the specific coin
    @param dom: etree created with an XPath
    @return: a list of wallets of the coin, or None if the coin doesn't have any
    """
    html = requests.get(coin_url)
    doc = lxml.html.fromstring(html.content)
    div_wallet = doc.xpath('//div[@class="coin-link-row tw-mb-0"]')[0]
    wallet = div_wallet.xpath('//span[@class="tw-self-start tw-py-1 tw-my-0.5 tw-min-w-3/10 2xl:tw-min-w-1/4'
                              ' tw-text-gray-500 dark:tw-text-white dark:tw-text-opacity-60 tw-mr-2"]/text()')

    # If the coin's link doesn't have the text 'Wallet' (i.e. doesn't have wallets), returns None
    if not wallet:
        return

    wallets = list()

    # There are three possible xPath for each coin, being two of them the same
    # except for one of the indexes that could be 4 or 5.
    for index_xpath in range(4, 6):
        index = 1
        try:
            # Appends all wallets of a coin until receiving an error when there are no more wallets to do so.
            while True:
                wallets.append(dom.xpath(f'/html/body/div[5]/div[4]/div[2]/div[2]/div[{index_xpath}]/div/a[{index}]')[-1].text)
                index += 1
        except IndexError:
            # Returns an empty list if no wallets where added in the loop before
            if index != 1:
                return wallets

    # This is the third possible XPath that a coin could have:
    try:
        wallets.append(dom.xpath(f'/html/body/div[5]/div[5]/div[2]/div[2]/div[5]/div/a')[-1].text)
        return wallets
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
    # Finds all coin's links
    scraped_links = soup.find_all('a', class_="tw-flex tw-items-start md:tw-flex-row tw-flex-col")

    list_of_coins = list()
    list_of_wallets = list()
    distinct_wallets = set()
    coin_id = 0
    df_historical = None

    print('Information being retrieved...')

    # Iterating over all the coins selected by the user
    for link in tqdm(scraped_links[f: t], total=t-f):
        coin_id += 1
        coin_name = link.findChild().text.strip()
        print(coin_name)
        coin_url = url + link['href']
        html_coin = get_soup(coin_url)
        dom = etree.HTML(str(html_coin))

        # Assigns to variables fictional None values that are supposed to change later
        price, market_cap, wallets_of_each_coin = (None, None, None)

        # Iterating over the price and the market cap.
        for value in range(2):
            # There are three possible xPath for each coin, being each one of them the same
            # except for one of the indexes that could be 4, 5, or 6.
            for index in range(4, 7):
                try:
                    if value == 0:
                        # Scrapes the price of a coin in the present
                        price = price_scraper(dom, index)
                    else:
                        # Scrapes the market cap of a coin in the present
                        market_cap = market_scraper(dom, index)
                    break
                except IndexError:
                    pass

        # Appends to a list all relevant information of a coin
        list_of_coins.append([coin_name, price, market_cap, coin_url])

        # URL of the historical data of a coin
        url_historical = coin_url + '/historical_data#panel'

        # Creates a csv file with the historical data of a coin
        csv_file = csv_reader(url_historical)

        # Creates a temporary dataframe with historical data of a coin
        temp_df = create_temp_df(coin_id, csv_file, days, date)

        # Assuming Bitcoin is the #1 coin. If the flippening was to happen, the code should be revised.
        # Creates the df_historical if it didn't exist; if it did, it concatenates itself with the temporary dataframe
        if coin_name == 'Bitcoin':
            df_historical = temp_df
        else:
            df_historical = pd.concat([df_historical, temp_df])

        # Creates a list of wallets of a coin
        wallets_of_each_coin = wallets_scraper(coin_url, dom)

        # If a coin has wallets (i.e. the list is not empty), appends to the list of wallets each one of them with
        # their respective coin id
        if wallets_of_each_coin:
            for wallet in wallets_of_each_coin:
                distinct_wallets.add(wallet)
                list_of_wallets.append([coin_id, wallet])

    # print(f'list of distinct wallets: {distinct_wallets}')

    # Creates the coins, wallets and distinct wallets dataframes and assigns an id column where necessary
    df_coins = pd.DataFrame(list_of_coins, columns=['coin_name', 'price', 'market_cap', 'URL'])
    df_coins['coin_id'] = range(1, len(df_coins) + 1)
    df_wallets = pd.DataFrame(list_of_wallets, columns=['coin_id', 'wallets'])
    df_distinct_wallets = pd.DataFrame(distinct_wallets, columns=['wallets'])
    df_distinct_wallets['wallet_id'] = range(1, len(df_distinct_wallets) + 1)

    # Changes the format of the price and market cap columns in the coins dataframe
    for column in ('price', 'market_cap'):
        df_coins[column] = df_coins[column].str.replace(',', '', regex=False)
        df_coins[column] = df_coins[column].str.replace('$', '', regex=False)
        df_coins[column] = df_coins[column].astype(float)

    # Changes the format of the price column in the historical data dataframe so it matches the one in coins dataframe
    df_historical['price'] = df_historical['price'].round(2)

    # Resets the index of the historical dataframe
    df_historical.reset_index(drop=True, inplace=True)

    # Shifts column 'coin_id' to the first position in df_coins and df_historical
    for dataframe in (df_coins, df_historical):
        first_column = dataframe.pop('coin_id')
        dataframe.insert(0, 'coin_id', first_column)

    #  TODO: change name of wallet in df_wallets to wallet_id

    print('\n')
    return df_coins, df_historical, df_wallets, df_distinct_wallets


def main():
    """
    Main function of the module:
    - checks all four possible arguments provided by the user have a correct value, giving an error message otherwise
    - calls the get_soup and web_scraper functions
    - returns three dataframes returned by the web_scraped function
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
    df_coins, df_historical, df_wallets, df_distinct_wallets = web_scraper(url, soup, f, t, days, date)

    return df_coins, df_historical, df_wallets, df_distinct_wallets
    # return df_coins, df_historical


if __name__ == '__main__':
    print(main())
    # coins, historical_data = main()
    # print(f"within CoinGecko:\n{coins}", end='\n\n')
    # # Saving to SQL
    # db = Database()
    # db.append_rows_to_coins(coins)
    # db.append_rows_to_history(historical_data)

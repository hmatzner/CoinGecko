import os
import requests
import argparse
import pandas as pd
import re
from bs4 import BeautifulSoup
from lxml import etree
from urllib.request import Request, urlopen
from datetime import datetime
from tqdm import tqdm


COINGECKO_URL = 'https://www.coingecko.com'

parser = argparse.ArgumentParser(description="Useful information: 'd' and 'D' are mutually exclusive and \
only one of them is expected at most.")
parser.add_argument('-k', '--coins', type=int, metavar='', help='Input how many coins, from 1 to 100, \
you would like to see (default: k=100).')

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


def csv_scraper(url_historical):
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


def temp_df_creator(coin_name, csv_file, days, date):
    """
    Creates a csv file of the coin's historical data, creates a temporary dataframe and removes the csv file.
    @param coin_name: name of the coin
    @param csv_file: csv format file of the coin's historical data
    @param days: argument passed by the user, specifies how many days of data to save in the dataframe
    @param date: argument passed by the user, specifies from which date of data to save in the dataframe
    @return: a temporary dataframe
    """
    with open(f'csv_{coin_name}', 'wb') as f:
        f.write(csv_file)

    if days is not None:
        temp_df = pd.read_csv(f'csv_{coin_name}').tail(days)
    elif date is not None:
        today = datetime.today()
        delta = (today - date).days + 1
        temp_df = pd.read_csv(f'csv_{coin_name}').tail(delta)
    else:
        temp_df = pd.read_csv(f'csv_{coin_name}')

    temp_df['Coin'] = coin_name
    os.remove(f'csv_{coin_name}')

    return temp_df


def web_scraper(url, soup, k, days, date):
    """
    Parses the data and creates a Pandas dataframe with the main information of each coin.
    Calls functions price_scraper, market_scraper, csv_scraper and temp_df_creator in the process.
    @param url: main webpage's url
    @param soup: Beautiful Soup object created with the requests module
    @param k: argument passed by the user, specifies the number of coins selected
    @param days: argument passed by the user, specifies how many days of data to save in the dataframe
    @param date: argument passed by the user, specifies from which date of data to save in the dataframe
    @return: a Pandas dataframe with relevant info about each coin and another one with their historical data
    """
    scraped_links = soup.find_all('a', class_="tw-flex tw-items-start md:tw-flex-row tw-flex-col")
    list_of_lists = list()
    df_historical = None
    print('Information being retrieved...')

    for link in tqdm(scraped_links[:k], total=k):
        coin_name = link.findChild().text.strip()
        # coin_name = coin.text.strip() We leave this piece of code here in case the class in the webpage is modified.

        coin_url = url + link['href']
        soup_coin = get_soup(coin_url)
        dom = etree.HTML(str(soup_coin))

        price, market_cap = (None, None)

        for value in range(2):
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

        csv_file = csv_scraper(url_historical)

        temp_df = temp_df_creator(coin_name, csv_file, days, date)

        # Assuming Bitcoin is the #1 coin. If the flippening was to happen, the code should be revised.
        if coin_name == 'Bitcoin':
            df_historical = temp_df
        else:
            df_historical = pd.concat([df_historical, temp_df])

    df = pd.DataFrame(list_of_lists, columns=['Coin', 'Price', 'Market Cap', 'URL'])
    df.index = range(1, len(df) + 1)
    df.reset_index(level=0, inplace=True)
    df.rename(columns={'index': '#'}, inplace=True)
    df.set_index('Coin', inplace=True)

    print('\n')
    return df, df_historical


def main():
    """
    Main function of the module:
    - checks all three possible arguments provided by the user have an expected value, giving an error message if needed
    - calls the get_soup and web_scraper functions
    - prints the two dataframes returned by the web_scraped function
    """
    # TODO: revise this docstring when finished.
    k = args.coins
    days = args.days
    date = args.date

    if k is None:
        k = 100
    if k not in range(1, 101):
        print("ERROR: The value of the argument 'coins' must be an integer from 1 to 100.")
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
    df, df_historical = web_scraper(url, soup, k, days, date)
    print(df)
    print('\n')
    print(df_historical)


if __name__ == '__main__':
    main()

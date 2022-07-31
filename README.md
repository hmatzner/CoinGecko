# CoinGecko

### Web scraping project to get information of the different cryptocurrencies

CoinGecko.com is a website containing information of thousands of different cryptocurrencies.
The top 100 coins have been selected and the website was scraped to get their current price, market cap and URL.

The user is expected to provide optional values for **n** (number of coins he wants to see, up to 100), and **d** (how many days of historical data) or **D** (from which date to see the historical data).

The main function when run returns information in two Pandas dataframes, one with information of the coins themselves and the other one with historical data of each one.
The script should be run on any python IDLE, check requirements.txt for further information.

Several libraries used are not specified in the requirements.txt file since they are built-in Python modules and there is no need to.

To install the dependencies needed for this file, run:

```
pip install -r requirements.txt
```

There are two versions of the file, .py (the main one) and .ipynb, being the latter one not updated and just builds a Pandas dataframe according to the 'milestone 1' of ITC's instructions.

*This repo is in 'milestone 2' stage and will keep being updated.*

For link to repo, [click here](https://github.com/hmatzner/CoinGecko).


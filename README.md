# CoinGecko

### Web scraping project to get information of the different cryptocurrencies

CoinGecko.com is a website containing information of thousands of different cryptocurrencies.
The top 100 coins have been selected and the website was scraped to get their current price, market cap and URL.

The user is expected to provide optional values for **f** and **t** (from and until which coin he wants to see, 
respectively, from 1 to 100), and **d** (how many days of historical data) or **D** (from which date to see the 
historical data).

The file webscraper.py when run by being imported in coingecko.py, returns information in four Pandas dataframes:
- one with information of the coins themselves,
- one with historical data of each one, 
- one with the connection between coins and wallets,
- and the last one with the wallets.

The script should be run on any python IDLE, check requirements.txt for further information.

Several libraries used are not specified in the requirements.txt file since they are built-in Python modules and there is 
no need to.

To install the dependencies needed for this file, run:

```
pip install -r requirements.txt
```

There are two versions of the file, .py (the main one) and .ipynb, being the latter one not updated and just builds a 
Pandas dataframe according to the 'milestone 1' of ITC's instructions.

Regarding the main branch which is the default one:
The main file that should be run on the terminal is coingecko.py, which imports:
- API.py, which performs a similar tasks in a single coin and times how long it took to perform the operation
- webscraper.py, which perform the web scraping and times how long it took to perform the operation (useful to compare 
with the time it took to API.py by running the code with the argparse arguments: -t1 -d0)
- and database.py, which performs the SQL queries.
The .ipynb is a discontinued version of the project

An ERD of the tables and their relationships used in database.py is included as ERD.png.

The main file coingecko.py is intended to be run from the CLI with the usage of argparse detailed before.

*This repo is in 'milestone 3' stage and will keep being updated.*

For link to repo, [click here](https://github.com/hmatzner/CoinGecko).

 

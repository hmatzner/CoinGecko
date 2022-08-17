import webscraper
from database_object2 import Database
import API


def main():
    # df_coins, df_historical, df_wallets, df_distinct_wallets = webscraper.main()
    Database(webscraper.main())
    print(API)


if __name__ == '__main__':
    main()

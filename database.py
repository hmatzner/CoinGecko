import pymysql
import pandas as pd
# import CoinGecko


class Database:
    DB_NAME = 'crypto_currencies'

    def __init__(self, df=None, df_hist=None, db_name=DB_NAME):
        """
        Initializes by creating the database and the tables
        @return: the connection and the cursor
        """
        self.PASSWORD = input("Provide a password for MySQL server: ")
        self.db_name = db_name
        self.cnx = None
        self.cursor = None

        self.create_connection(use_db=False)
        self.create_database()

        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        if ('coins',) not in tables:
            self.create_coins_table()
        else:
            print("Coins table already existed")
        if ('history',) not in tables:
            self.create_history_table()
        else:
            print("History table already existed")

        if df:
            self.append_rows_to_coins(df)
        if df_hist:
            self.append_rows_to_coins(df_hist)

    def create_connection(self, use_db=True):
        """
        Creates and returns a connection and a cursor
        @param db_name: name of the database
        """
        if use_db:
            self.cnx = pymysql.connect(host='localhost',
                                       user='root',
                                       password=self.PASSWORD,
                                       database=self.DB_NAME)
            self.cursor = self.cnx.cursor()
        else:
            self.cnx = pymysql.connect(host='localhost',
                                       user='root',
                                       password=self.PASSWORD)
            self.cursor = self.cnx.cursor()

    def create_database(self):
        """
        Creates the database
        @param name: name of the database
        """
        self.cursor.execute("SHOW DATABASES")
        database_existed = self.cursor.fetchall()
        if ('crypto_currencies',) in database_existed:
            print("Database already exists")
            self.cursor.execute(f"USE {self.db_name}")
        else:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.DB_NAME}")
            self.cnx.commit()
            print("Database created")
            self.cursor.execute(f"USE {self.DB_NAME}")

    def create_coins_table(self):
        """
        Creates the table 'coins' in the database
        @param cnx: connection
        @param cursor: cursor to execute queries
        """
        query = """CREATE TABLE IF NOT EXISTS coins
                        (ID int NOT NULL PRIMARY KEY, coin varchar(45), price varchar(45),
                         market_cap varchar(45), coin_url varchar(45))"""
        self.cursor.execute(query)
        self.cnx.commit()
        print("Coins table created")
        self.update_coins_list()

    def create_history_table(self):
        """
        Creates the table 'history' in the database
        @param cnx: connection
        @param cursor: cursor to execute queries
        """
        query = """CREATE TABLE IF NOT EXISTS history
                        (ID int, date varchar(45), price varchar(45),
                         market_cap varchar(45), volume_of_flow varchar(45),
                         FOREIGN KEY (ID) REFERENCES coins(ID))"""
        self.cursor.execute(query)
        self.cnx.commit()
        print("History table created")

    def append_rows_to_coins(self, data):
        """
        Gets the data as a Pandas dataframe with columns:
        ['index', 'coin_name', 'price', 'market_cap', 'URL'].
        Inserts it into the 'coins' table
        @param cnx: connection
        @param cursor: cursor to execute queries
        @param data: Pandas dataframe
        """
        self.cursor.execute("SELECT coin From coins")
        coins = [coin[0] for coin in self.cursor.fetchall()]
        print(coins)
        # data['coin_name'] = data['coin_name'].str.replace(' ', '-')
        # print(data)
        index_of_existing_coins = data.coin_name.isin(coins)
        # pd.Series([coin not in self.coins for coin in data['coin_name']])
        print(index_of_existing_coins)
        data_to_append = data[~index_of_existing_coins]
        data_to_update = data[index_of_existing_coins]

        query = """INSERT INTO coins (ID, coin, price, market_cap, coin_url)
                        VALUES (%s, %s, %s, %s, %s)"""
        data = data_to_append.values.tolist()
        self.cursor.executemany(query, data)
        self.cnx.commit()
        print(f"{len(data_to_append)} rows were successfully uploaded")

        query = """UPDATE coins
                        SET price = %(price)s, market_cap = %(market_cap)s
                        WHERE coin = %(coin_name)s"""
        data = data_to_update.to_dict('records')
        print(data)
        self.cursor.executemany(query, data)
        self.cnx.commit()
        # # except:
        # #     pass
        # self.update_coins_list()

    def append_rows_to_history(self, data):
        """
        Gets the data as a Pandas dataframe with columns:
        ['snapped_at', 'price', 'market_cap', 'total_volume', 'coin_id'].
        Inserts it into the 'history' table
        @param cnx: connection
        @param cursor: cursor to execute queries
        @param data: Pandas dataframe
        """
        data.fillna(method='ffill', inplace=True)
        data = data.to_dict('records')
        query = """REPLACE INTO history (ID, price, market_cap, volume_of_flow, date)
                       VALUES (%(coin_id)s, %(price)s, %(market_cap)s, %(total_volume)s, %(snapped_at)s)"""
        try:
            self.cursor.executemany(query, data)
            self.cnx.commit()
            print(f"{len(data)} rows were successfully uploaded to the history table")
        except:
            print("ERROR: could not append rows to the history table")

    def show_tables(self):
        """
        Prints the tables inside the database
        @param cnx: connection
        @param cursor: cursor to execute queries
        """
        self.cursor.execute("SHOW TABLES")
        print(self.cursor.fetchall())

    def show_table(self, table_name):
        """
        Prints the content of the table provided
        @param cnx: connection
        @param cursor: cursor to execute queries
        @param table_name: table provided from the database
        """
        self.cursor.execute(f"SELECT * FROM {table_name}")
        print(f"Content of {table_name}")
        print(self.cursor.fetchall())

    def close_connection(self):
        """
        Performs the commit and closes the connection
        @param cnx: connection
        @param cursor: cursor to execute queries
        """
        self.cursor.close()
        self.cnx.close()
        print("Connection closed")

    # def main(df, df_hist):
    #     cnx, cursor = init()
    #     df_hist.fillna(method='ffill', inplace=True)
    #     append_rows_to_coins(cnx, cursor, df)
    #     append_rows_to_history(cnx, cursor, df_hist)
    #     close_connection(cnx, cursor)

    # if __name__=='__main__':
    #     pass
    # df, df_hist = CoinGecko.main()
    # df_hist.fillna(method='ffill', inplace=True)
import pymysql
import pandas as pd
import time


class Database:
    DB_NAME = 'crypto_currencies'

    def __init__(self, coins=None, hist=None, wallets=None, wallets_names=None, db_name=DB_NAME, logger=None):
        """
        Initializes the class by creating the database and the tables
        @param coins: coins dataframe
        @param hist: historical data dataframe
        @param wallets: connection between wallets and coins dataframe
        @param wallets_names: unique wallets dataframe
        @param db_name: name of the database
        @param logger: logger object
        """
        start = time.perf_counter()
        try:
            with open('.gitignore_folder/password.txt') as f:
                self.PASSWORD = f.read()
        except FileNotFoundError:
            # try:
            #     with open('ps.txt') as f:
            #         self.PASSWORD = f.read()
            # except FileNotFoundError:
            self.PASSWORD = input("Provide password for MySQL server: ")

        self.db_name = db_name
        self.logger = logger
        self.connection = self.create_connection(use_db=False)
        self.cursor = self.connection.cursor()
        self.create_database()

        tables = pd.read_sql("SHOW TABLES", self.connection).Tables_in_crypto_currencies.to_list()

        if 'coins' not in tables:
            self.create_coins_table()
        else:
            self.logger.info("Coins table already existed")
        if 'history' not in tables:
            self.create_history_table()
        else:
            self.logger.info("History table already existed")
        if 'wallets' not in tables:
            self.create_wallets_table()
        else:
            self.logger.info("Wallets table already existed")
        if 'wallets_names' not in tables:
            self.create_wallets_names_table()
        else:
            self.logger.info("Wallets names table already existed")

        if coins is not None:
            self.append_rows_to_coins(coins)
        if hist is not None:
            self.append_rows_to_history(hist)
        if wallets is not None:
            self.append_rows_to_wallets(wallets)
        if wallets_names is not None:
            self.append_rows_to_wallets_names(wallets_names)

        end = time.perf_counter()
        print(f'Time taken to store data in SQL: {end - start} seconds.\n')

    def create_connection(self, use_db=True):
        """
        Creates and returns a connection
        @param use_db: if True uses the db_name as the database in the connection, otherwise it doesn't use one
        """
        if use_db:
            return pymysql.connect(host='localhost',
                                   user='root',
                                   password=self.PASSWORD,
                                   database=self.DB_NAME)
        else:
            return pymysql.connect(host='localhost',
                                   user='root',
                                   password=self.PASSWORD)

    def create_database(self):
        """
        Creates a database named like db_name variable
        """
        self.cursor.execute("SHOW DATABASES")
        database_existed = self.cursor.fetchall()

        if (self.db_name,) in database_existed:
            self.logger.info("Database already exist")
            self.cursor.execute(f"USE {self.db_name}")
        else:
            self.cursor.execute(f"CREATE DATABASE {self.DB_NAME}")
            self.connection.commit()
            self.logger.info("Database created")
            self.cursor.execute(f"USE {self.DB_NAME}")

    def create_coins_table(self):
        """
        Creates the 'coins' table in the database
        """
        query = """CREATE TABLE IF NOT EXISTS coins
                    (ID int NOT NULL PRIMARY KEY, coin_name varchar(45), price varchar(45),
                     market_cap varchar(45), coin_url varchar(45))"""

        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info("coins table created")

    def create_history_table(self):
        """
        Creates the 'history' table in the database
        """
        query = """CREATE TABLE IF NOT EXISTS history
                    (ID int, date varchar(45), price varchar(45),
                     market_cap varchar(45), volume_of_flow varchar(45),
                     FOREIGN KEY (ID) REFERENCES coins(ID))"""

        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info("history table created")

    def create_wallets_table(self):
        """
        Creates the 'wallets' table in the database
        """
        query = """CREATE TABLE wallets
                    (coin_id int, wallet_id int)"""

        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info("wallets table created")

    def create_wallets_names_table(self):
        """
        Creates the 'wallets_names' table in the database
        """
        query = """CREATE TABLE wallets_names
                    (wallet_id int NOT NULL PRIMARY KEY, wallet_name varchar(45))"""

        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info("wallets_names table created")

    def append_rows_to_coins(self, data):
        """
        Separates new data from other that already existed in the coins table
        Inserts the new rows and updates the existing ones
        @param data: coins dataframe
        """
        query = "SELECT coin_name FROM coins"
        existing_coins = pd.read_sql(query, self.connection).coin_name
        index_of_existing_coins = data.coin_name.isin(existing_coins)

        data_to_append = data[~index_of_existing_coins]
        data_to_update = data[index_of_existing_coins]

        query = """INSERT INTO coins (ID, coin_name, price, market_cap, coin_url)
                    VALUES (%s, %s, %s, %s, %s)"""
        data = data_to_append.values.tolist()

        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.logger.info(f"{len(data_to_append)} rows were successfully uploaded")
        except Exception as e:
            self.logger.info(e)

        query = """UPDATE coins
                    SET price = %(price)s, market_cap = %(market_cap)s
                    WHERE coin_name = %(coin_name)s"""

        data = data_to_update.to_dict('records')

        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.logger.info(f"{len(data_to_update)} rows were successfully updated")
        except Exception as e:
            self.logger.info(e)

    def append_rows_to_history(self, data):
        """
        Gets the data as a Pandas dataframe with columns:
        ['coin_id', 'total_volume', 'price', 'market_cap', 'snapped_at'].
        Inserts it into the 'history' table
        @param data: Pandas dataframe
        """
        data.fillna(method='ffill', inplace=True)
        data = data.to_dict('records')
        query = """REPLACE INTO history (ID, price, market_cap, volume_of_flow, date)
                   VALUES (%(coin_id)s, %(price)s, %(market_cap)s, %(total_volume)s, %(snapped_at)s)"""

        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.logger.info(f"{len(data)} rows were successfully uploaded to the history table")
        except Exception as e:
            self.logger.info(e)

    def append_rows_to_wallets(self, data):
        """
        Gets the data as a Pandas dataframe with columns:
        ['coin_id', 'wallet_id'].
        Inserts it into the 'wallets' table
        @param data: Pandas dataframe
        """
        data = data.to_dict('records')
        query = """INSERT INTO wallets (coin_id, wallet_id)
                    VALUES (%(coin_id)s, %(wallet_id)s)"""

        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.logger.info(f"{len(data)} rows were successfully uploaded to the wallets table")
        except Exception as e:
            self.logger.info(e)

    def append_rows_to_wallets_names(self, data):
        """
        Gets the data as a Pandas dataframe with columns:
        ['wallet_name', 'wallet_id'].
        Inserts it into the 'wallets_name' table
        @param data: Pandas dataframe
        """
        data = data.to_dict('records')
        query = """INSERT INTO wallets_names (wallet_id, wallet_name)
                    VALUES (%(wallet_id)s, %(wallet_name)s)"""

        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.logger.info(f"{len(data)} rows were successfully uploaded to the wallets_names table")
        except Exception as e:
            self.logger.info(e)

    def close_connection(self):
        """
        Closes the cursor and the connection.
        """
        self.cursor.close()
        self.connection.close()
        self.logger.info("Connection closed")

import pymysql
import pandas as pd


class Database:
    DB_NAME = 'crypto_currencies'

    def __init__(self, coins=None, hist=None, wallets=None, wallets_names=None, db_name=DB_NAME, logger=None):
        """
        Initializes by creating the database and the tables
        If given dataframes it will insert them to the relevant tables
        """
        try:
            with open('.gitignore_folder/password.txt') as f:
                self.PASSWORD = f.read()
        except FileNotFoundError:
            self.PASSWORD = input("provide password for mySQL server: ")

        self.db_name = db_name
        self.logger = logger
        self.connection = self.create_connection(use_db=False)
        self.cursor = self.connection.cursor()
        self.create_database()

        # logger.info(pd.read_sql("SHOW TABLES", self.connection).Tables_in_crypto_currencies)

        tables = pd.read_sql("SHOW TABLES", self.connection).Tables_in_crypto_currencies.to_list()

        if 'coins' not in tables:
            self.create_coins_table()
        else:
            self.logger.info("coins table was already existed")
        if 'history' not in tables:
            self.create_history_table()
        else:
            self.logger.info("history table was already existed")
        if 'wallets' not in tables:
            self.create_wallets_table()
        else:
            self.logger.info("wallets table was already existed")
        if 'wallets_names' not in tables:
            self.create_wallets_names_table()
        else:
            self.logger.info("wallets_names table was already existed")

        if coins is not None:
            print(f"(database)coins: \n{type(coins)}")
            self.append_rows_to_coins(coins)
        if hist is not None:
            self.append_rows_to_history(hist)
        if wallets is not None:
            self.append_rows_to_wallets(wallets)
        if wallets_names is not None:
            self.append_rows_to_wallets_names(wallets_names)

    def create_connection(self, use_db=True):
        """
        Creates and returns a connection
        @param usd_db: if True uses {DB_NAME} as the database in the connection, otherwise doe'snt use database
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
        Creates a database named {db_name}
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
        Creates the table 'coins' in the database
        """
        query = """CREATE TABLE IF NOT EXISTS coins
                    (ID int NOT NULL PRIMARY KEY, coin_name varchar(45), price varchar(45),
                     market_cap varchar(45), coin_url varchar(45))"""
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info("coins table created")

    def create_history_table(self):
        """
        Creates a table called 'history' in the database
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
        Creates a table called 'wallets' in the database
        """
        query = """CREATE TABLE wallets
                    (coin_id int, wallet_id int)"""
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info("wallets table created")

    def create_wallets_names_table(self):
        """
        Creates a table called 'wallets_names' in the database
        """
        query = """CREATE TABLE wallets_names
                    (wallet_id int NOT NULL PRIMARY KEY, wallet_name varchar(45))"""
        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info("wallets_names table created")

    def append_rows_to_coins(self, data):
        """
        :data: DataFrame of coins
        Seperates new data and data that is already in the coins table,
        Inserts the new data and updates the existings
        """
        query = "SELECT coin_name From coins"
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
        """closes the cursor and the connection.
            Good Night."""
        self.cursor.close()
        self.connection.close()
        self.logger.info("connection closed")
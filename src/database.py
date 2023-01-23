import pymysql
import pandas as pd
from logger import logger
import warnings

warnings.filterwarnings("ignore")


class Database:
    logger = logger('database')

    def __init__(self, init):
        """
        Initializes the class by creating the database and the tables
        """
        # self.logger = logger
        try:
            self.conf = pd.read_json('configurations.json').db
        except FileNotFoundError:
            self.logger.error("configurations.json not found")

        # start = time.perf_counter()

        self.connection = self.create_connection(use_db=True)
        self.cursor = self.connection.cursor()

        if init:
            # self.create_database()
            self.create_tables()

        # end = time.perf_counter()
        # print(f'Time taken to store data in SQL: {end - start} seconds.\n')

    def create_connection(self, use_db=True):
        """
        Creates and returns a connection
        @param use_db: if True uses the db_name as the database in the connection, otherwise it doesn't use one
        """
        if use_db:
            return pymysql.connect(host=self.conf.host,
                                   user=self.conf.user,
                                   password=self.conf.password,
                                   database=self.conf['name'])
        else:
            return pymysql.connect(host=self.conf.host,
                                   user=self.conf.user,
                                   password=self.conf.password)

    def create_database(self):
        """
        Creates a database named like db_name variable
        """
        database_existed = pd.read_sql("SHOW DATABASES", self.connection)

        if self.conf['name'] in database_existed.values:
            self.logger.info("Database already exist; Deleting it and creating new from scratch")
            self.cursor.execute(f"DROP DATABASE {self.conf['name']}")
            self.connection.commit()

        self.cursor.execute(f"CREATE DATABASE {self.conf['name']}")
        self.connection.commit()
        self.logger.info("Database created")
        self.cursor.execute(f"USE {self.conf['name']}")

    def create_tables(self):
        """
        Initializes four tables:
        Updating data will be stored in coins
        Historical data will be stored in history
        Information about wallets will be stored in wallets
        Connections between coins and wallets will be stored in wallets names
        """
        tables = pd.read_sql("SHOW TABLES", self.connection).Tables_in_dor_hernan.values
        for table in tables[::-1]:
            self.cursor.execute(f"DROP TABLE {table}")
        self.create_coins_table()
        self.create_history_table()
        self.create_wallets_table()
        self.create_wallets_names_table()

    def create_coins_table(self):
        """
        Creates the 'coins' table in the database
        """
        query = """CREATE TABLE coins
                    (ID int AUTO_INCREMENT PRIMARY KEY, coin_name varchar(45), price varchar(45),
                     market_cap varchar(45), coin_url varchar(65), timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)"""

        self.cursor.execute(query)
        self.connection.commit()
        self.logger.info("coins table created")

    def create_history_table(self):
        """
        Creates the 'history' table in the database
        """
        query = """CREATE TABLE history
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

    def update_all(self, dict_):
        """
        Gets a dictionary, updates the tables
        :keys: names of tables
        :values: dataframes to be updated
        """
        matcher = {'coins': self.update_coins,
                   'hist': self.update_history,
                   'wallets': self.update_wallets,
                   'wallets_names': self.update_wallets_names}
        for k, v in dict_.items():
            matcher[k](v)

    def update_coins(self, data):
        """
        Separates new data from other that already existed in the coins table
        Inserts the new rows and updates the existing ones
        @param data: coins dataframe
        """
        # print(data.drop(columns=['coin_id']))

        query = """INSERT INTO coins (coin_name, price, market_cap, coin_url)
                    VALUES (%s, %s, %s, %s)"""
        try:
            self.cursor.executemany(query, data.drop(columns=['coin_id']).values.tolist())
            self.connection.commit()
            self.logger.info(f"{len(data)} rows were successfully uploaded")
        except Exception as e:
            self.logger.info(e)

    def update_history(self, data):
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

    def update_wallets(self, data):
        """
        Gets the data as a Pandas dataframe with columns:
        ['coin_id', 'wallet_id'].
        Inserts it into the 'wallets' table
        @param data: Pandas dataframe
        """
        query = "SELECT * FROM wallets"
        existing_rows = pd.read_sql(query, self.connection)
        if len(existing_rows) > 0:
            data = data.merge(existing_rows, on=data.columns, how='left')
            # .query(
            # "_merge != 'both'").drop('_merge', axis=1).reset_index(drop=True)
            # print(data)

        data = data.to_dict('records')
        query = """INSERT INTO wallets (coin_id, wallet_id)
                            VALUES (%(coin_id)s, %(wallet_id)s)"""

        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            self.logger.info(f"{len(data)} rows were successfully uploaded to the wallets table")
        except Exception as e:
            self.logger.info(e)

    def update_wallets_names(self, data):
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

    def show_coins(self):
        """
        Prints the coins tables
        """
        print(pd.read_sql("SELECT * FROM coins", self.connection)[['coin_name', 'price', 'timestamp']])

    def close_connection(self):
        """
        Closes the cursor and the connection.
        """
        self.cursor.close()
        self.connection.close()
        self.logger.info("Connection closed")

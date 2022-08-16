import pymysql
import pandas as pd


class Database:
    DB_NAME = 'crypto_currencies'

    def __init__(self, df=None, df_hist=None, db_name=DB_NAME):
        try:
            with open('.gitignore_folder\password.txt') as f:
                self.PASSWORD = f.read()
        except FileNotFoundError:
            self.PASSWORD = input("provide password for mySQL server: ")
        self.db_name=db_name
        
        self.connection = self.create_connection(use_db=False)
        self.cursor = self.connection.cursor()
        self.create_database()
        
        self.cursor.execute("SHOW TABLES")
        tables = self.cursor.fetchall()
        if ('coins',) not in tables:
            self.create_coins_table()
        else:
            print("coins table was already existed")
        if ('history',) not in tables:
            self.create_history_table()
        else:
            print("history table was already existed")
        
        if df:
            self.append_rows_to_coins(df)
        if df_hist:
            self.append_rows_to_history(df_hist)

    def create_connection(self, use_db=True):
        """creates and returns a connection and a cursor"""
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
        self.cursor.execute("SHOW DATABASES")
        database_existed = self.cursor.fetchall()
        if (self.db_name, ) in database_existed:
            print ("Database already exist")
            self.cursor.execute(f"USE {self.db_name}")
        else:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.DB_NAME}")
            self.connection.commit()
            print("Database created")
            self.cursor.execute(f"USE {self.DB_NAME}")

    def create_coins_table(self):
        # if
        query = """CREATE TABLE IF NOT EXISTS coins
                    (ID int NOT NULL PRIMARY KEY, coin_name varchar(45), price varchar(45),
                     market_cap varchar(45), coin_url varchar(45))"""
        self.cursor.execute(query)
        self.connection.commit()
        print("coins table created")
        
    def create_history_table(self):
        query = """CREATE TABLE IF NOT EXISTS history
                    (ID int, date varchar(45), price varchar(45),
                     market_cap varchar(45), volume_of_flow varchar(45),
                     FOREIGN KEY (ID) REFERENCES coins(ID))"""
        self.cursor.execute(query)
        self.connection.commit()
        print("history table created")

    def append_rows_to_coins(self, data):
        """
        :data: DataFrame of coins
        """
        # self.cursor.execute("SELECT coin From coins")
        # coins = [coin[0] for coin in self.cursor.fetchall()]
        # print(coins)
        # data['coin_name'] = data['coin_name'].str.replace(' ', '-')
        print(f"data:\n{data}", end='\n\n')
        query = "SELECT coin_name From coins"
        existing_coins = pd.read_sql(query, self.connection).coin_name

        print(f"coins already in table: \n{existing_coins}", end='\n\n')

        index_of_existing_coins = data.coin_name.isin(existing_coins)

        # pd.Series([coin not in self.coins for coin in data['coin_name']])
        print(f"existing coins: {data.loc[index_of_existing_coins, :]}")
        data_to_append = data[~index_of_existing_coins]
        data_to_update = data[index_of_existing_coins]
        
        query = """INSERT INTO coins (ID, coin_name, price, market_cap, coin_url)
                    VALUES (%s, %s, %s, %s, %s)"""
        data = data_to_append.values.tolist()
        self.cursor.executemany(query, data)
        self.connection.commit()
        print (f"{len(data_to_append)} rows were successfully uploaded")
        
        query = """UPDATE coins
                    SET price = %(price)s, market_cap = %(market_cap)s
                    WHERE coin_name = %(coin_name)s"""
        data = data_to_update.to_dict('records')
        print(f"coins to update:\n{data}")
        self.cursor.executemany(query, data)
        self.connection.commit()
        print(f"{len(data_to_update)} rows were successfully updated")

    def append_rows_to_history(self, data):
        data.fillna(method='ffill', inplace=True)
        data = data.to_dict('records')
        query = """REPLACE INTO history (ID, price, market_cap, volume_of_flow, date)
                   VALUES (%(coin_id)s, %(price)s, %(market_cap)s, %(total_volume)s, %(snapped_at)s)"""
        try:
            self.cursor.executemany(query, data)
            self.connection.commit()
            print (f"{len(data)} rows were successfully uploaded to the history table")
        except:
            print ("appending to history didn't successed")        
        
    def show_tables(self):
        self.cursor.execute("SHOW TABLES")
        print(self.cursor.fetchall())
    
    def show_table(self, table_name):
        self.cursor.execute(f"SELECT * FROM {table_name}")
        print(f"content of {table_name}")
        print(self.cursor.fetchall())
    
    def close_connection(self):
        self.cursor.close()
        self.connection.close()
        print ("connection closed")
    
# def main(df, df_hist):
#     connection, cursor = init()
#     df_hist.fillna(method='ffill', inplace=True)
#     append_rows_to_coins(connection, cursor, df)
#     append_rows_to_history(connection, cursor, df_hist)
#     close_connection(connection, cursor)


# if __name__=='__main__':
#     pass
    # df, df_hist = CoinGecko.main()
    # df_hist.fillna(method='ffill', inplace=True)

db = Database()
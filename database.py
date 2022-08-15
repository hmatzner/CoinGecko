import pymysql
import pandas as pd


PASSWORD = input("provide password for mySQL server:\n")
DB_NAME = 'crypto_currencies'


def create_connection(db_name=DB_NAME):
    """creates and returns a connection and a cursor"""
    cnx2 = pymysql.connect(host='localhost',
                           user='root',
                           password=PASSWORD,
                           database=db_name)
    cursor2 = cnx2.cursor()
    return cnx2, cursor2


def create_database(cnx, cursor, name=DB_NAME):
    "creates databse"
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name}")
    cnx.commit()


def create_coins_table(cnx, cursor):
    "creates the table 'coins' in database {DB_NAME}"
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE IF NOT EXISTS coins
            (ID int NOT NULL PRIMARY KEY, coin varchar(45), price varchar(45),
            market_cap varchar(45), coin_url varchar(45))"""
    cursor.execute(query)
    cnx.commit()


def append_rows_to_coins(cnx, cursor, data):
    """
    gets data as as pd.DataFrame with columns:
        ['index', 'coin_name', 'price', 'market_cap', 'URL']
    and inserts it to the 'coins' table
    """
    data = data.values.tolist()
    print(data)
    query = """REPLACE INTO coins (ID, coin, price, market_cap, coin_url)
               VALUES (%s, %s, %s, %s, %s)"""
    try:
        cursor.executemany(query, data)
        cnx.commit()
        print(f"{len(data)} rows were successfully uploaded")
    except:
        print("it didn't upload correctly")


def create_history_table(cnx, cursor):
    "creates the table 'history' in database {DB_NAME}"
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE IF NOT EXISTS history
            (ID int, date varchar(45), price varchar(45),
            market_cap varchar(45), volume_of_flow varchar(45),
            FOREIGN KEY (ID) REFERENCES coins(ID))"""
    cursor.execute(query)
    cnx.commit()


def append_rows_to_history(cnx, cursor, data):
    """
    gets data as as pd.DataFrame with columns:
        ['snapped_at', 'price', 'market_cap', 'total_volume', 'coin_id']
    and inserts it to the 'history' table
    """
    data = data.to_dict('records')
    query = """REPLACE INTO history (ID, price, market_cap, volume_of_flow, date)
               VALUES (%(coin_id)s, %(price)s, %(market_cap)s, %(total_volume)s, %(snapped_at)s)"""
    try:
        cursor.executemany(query, data)
        cnx.commit()
        print(f"{len(data)} rows were successfully uploaded to the history table")
    except:
        print("it didn't upload correctly")


def show_tables(cnx, cursor):
    "prints the tables inside {DB_NAME}"
    cursor.execute(f"USE {DB_NAME}")
    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())


def show_table(cnx, cursor, table_name):
    "prints content of the table {table_name}"
    cursor.execute(f"SELECT * FROM {table_name}")
    print(f"content of {table_name}")
    print(cursor.fetchall())


def close_connection(cnx, cursor):
    "closes connection, commit first"
    cnx.commit()
    cursor.close()


def init():
    """
    initialize:
    creates the database and the tables
    returns connection and cursor
    """
    cnx = pymysql.connect(host='localhost',
                          user='root',
                          password=PASSWORD)
    cursor = cnx.cursor()
    try:
        create_database(cnx, cursor)
        cnx.commit()
        close_connection(cnx, cursor)
        print("DB created")
    except:
        print("DB existed already")
    cnx, cursor = create_connection()
    try:
        create_coins_table(cnx, cursor)
    except:
        pass

    try:
        create_history_table(cnx, cursor)
    except:
        pass
    return cnx, cursor


def main(df, df_hist):
    """"
    gets 2 dataframes from CoinGecko.py,
    fills empty cells with the above value
    """
    cnx, cursor = init()
    df_hist.fillna(method='ffill', inplace=True)
    append_rows_to_coins(cnx, cursor, df)
    append_rows_to_history(cnx, cursor, df_hist)
    close_connection(cnx, cursor)
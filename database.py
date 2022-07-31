import pymysql
import pandas as pd

PASSWORD = input("provide password for mySQL server:\n")

DB_NAME = 'crypto_currencies'
cnx = pymysql.connect(host='localhost',
                      user='root',
                      password=PASSWORD)
cursor = cnx.cursor()


def create_connection(db_name=DB_NAME):
    """creates and returns a connection and a cursor"""
    cnx2 = pymysql.connect(host='localhost',
                           user='root',
                           password=PASSWORD,
                           database=db_name)
    cursor2 = cnx.cursor()
    return cnx2, cursor2


def create_database(name=DB_NAME):
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name}")


def create_coins_table(cnx, cursor):
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE IF NOT EXISTS coins
            (ID int NOT NULL PRIMARY KEY, coin varchar(45), price varchar(45),
            market_cap varchar(45), coin_url varchar(45))"""
    cursor.execute(query)
    cnx.commit()


def append_rows_to_coins(cnx, cursor, data):
    data = data.values.tolist()
    query = """REPLACE INTO coins (ID, coin, price, market_cap, coin_url)
               VALUES (%s, %s, %s, %s, %s)"""
    try:
        cursor.executemany(query, data)
        print(f"{len(data)} rows were successfully uploaded")
    except:
        print("it didn't upload correctly")
    cnx.commit()


def create_history_table(cnx, cursor):
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE history
            (ID int, date varchar(45), price varchar(45),
            market_cap varchar(45), volume_of_flow varchar(45),
            FOREIGN KEY (ID) REFERENCES coins(ID))"""
    cursor.execute(query)
    cnx.commit()


def append_rows_to_history(cnx, cursor, data):
    data = data.to_dict('records')
    print(data[:3])
    query = """REPLACE INTO history (ID, price, market_cap, volume_of_flow, date)
               VALUES (%(coin_id)s, %(price)s, %(market_cap)s, %(total_volume)s, %(snapped_at)s)"""
    try:
        cursor.executemany(query, data)
        print(f"{len(data)} rows were successfully uploaded to the history table")
    except:
        print("it didn't upload correctly")
    cnx.commit()


def show_tables(cnx, cursor):
    cursor.execute(f"USE {DB_NAME}")
    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())


def show_table(cnx, cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    print(f"content of {table_name}")
    print(cursor.fetchall())


def close_connection(cnx, cursor):
    cnx.commit()
    cursor.close()


def init():
    cnx = pymysql.connect(host='localhost',
                          user='root',
                          password=PASSWORD)
    cursor = cnx.cursor()
    try:
        create_database()
        close_connection(cnx, cursor)
        print("DB created")
    except:
        print("didn't created DB")
    cnx, cursor = create_connection()
    try:
        create_coins_table(cnx, cursor)
    except:
        print("didn't created coins")

    try:
        create_history_table(cnx, cursor)
    except:
        print("didn't created history")
    cnx.commit()
    return cnx, cursor


def main(df, df_hist):
    cnx, cursor = init()
    df_hist.fillna(method='ffill', inplace=True)
    append_rows_to_coins(cnx, cursor, df)
    append_rows_to_history(cnx, cursor, df_hist)
    close_connection(cnx, cursor)

import pymysql
import mysql.connector
import pandas as pd
# import CoinGecko

DB_NAME = 'crypto_currencies'


cnx = pymysql.connect(host='localhost',
                      user='root',
                      password='kaBoom93')
cursor = cnx.cursor()


def create_database(name=DB_NAME):
    global cnx, cursor
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name}")
    cnx = pymysql.connect(host='localhost',
                      user='root',
                      password='kaBoom93',
                      database=name)
    cursor = cnx.cursor()
    

    
def create_coins_table():
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE IF NOT EXISTS coins
            (coin varchar(45) PRIMARY KEY, price float,
            market_cap float, coin_url varchar(45))"""
    cursor.execute(query)
    
    
def append_rows_to_coins(data):
    if type(data) == pandas.core.frame.DataFrame:
        data = example_df.values.tolist()
    query = """INSERT INTO coins (coin, price, market_cap, coin_url)
               VALUES (%s, %s, %s, %s)"""
    try:
        cursor.executemany(query, data)
        print (f"{len(data)} rows were successfully uploaded")
    except:
        print ("it didn't upload correctly")
        
        
def show_tables():
    cursor.execute(f"USE {DB_NAME}")
    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())
    

def close_connection():
    cursor.close()

# df = ... 
        
# example_df = pd.DataFrame(['Bit', 600, 12000, 'www.bit.com'])


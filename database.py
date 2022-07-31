import pymysql
import mysql.connector
import pandas as pd
from os.path import exists
from os import getcwd
from datetime import date
# import CoinGecko


pwd_path = getcwd()+"\.gitignore\password.txt"
if exists(exists(pwd_path)):
    with open(pwd_path) as f:
        PASSWORD = f.readline()
else:
    PASSWORD = input("provide password for mySQL server:\n")

DB_NAME = 'crypto_currencies'


cnx = pymysql.connect(host='localhost',
                      user='root',
                      password=PASSWORD)
cursor = cnx.cursor()

def create_connection(db_name=None):
    global cnx, cursor
    cnx = pymysql.connect(host='localhost',
                      user='root',
                      password=PASSWORD,
                      database=db_name)
    cursor = cnx.cursor()
    

def create_database(name=DB_NAME):
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name}")
    create_connection(DB_NAME)
    
    
    
def create_coins_table():
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE IF NOT EXISTS coins
            (ID int NOT NULL PRIMARY KEY, coin varchar(45), price varchar(45),
            market_cap varchar(45), coin_url varchar(45))"""
    cursor.execute(query)
    
    
def append_rows_to_coins(data):
    """"""
    if type(data) == pd.core.frame.DataFrame:
        data = data.values.tolist()
    query = """INSERT INTO coins (ID, coin, price, market_cap, coin_url)
               VALUES (%s, %s, %s, %s, %s)"""
    try:
        cursor.executemany(query, data)
        print (f"{len(data)} rows were successfully uploaded")
    except:
        print ("it didn't upload correctly")


def create_history_table():
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE history
            (ID int, price varchar(45),
            market_cap varchar(45), volume_of_flow varchar(45),
            date Date,
            FOREIGN KEY (ID) REFERENCES coins(ID))"""
    cursor.execute(query)
    
    
def append_rows_to_history(data):
    data = data.to_dict('records')
    print(data)
    query = """INSERT INTO history (ID, price, market_cap, volume_of_flow, date)
               VALUES (%(ID)s, %(price)s, %(market_cap)s, %(total_volume)s, %(snapped_at)s)"""
    try:
        cursor.executemany(query, data)
        print (f"{len(data)} rows were successfully uploaded to the history table")
    except:
        print ("it didn't upload correctly")
        
        
def show_tables():
    cursor.execute(f"USE {DB_NAME}")
    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())
    
    
def show_table(table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    print(f"content of {table_name}")
    print(cursor.fetchall())
    

def close_connection():
    cnx.commit()
    cursor.close()
    

def test_add_rows():
    df1 = pd.DataFrame([[1, 'Bit', '35$', '350$', 'www.bit.com'], [2, 'Cit', '15$', '250$', 'www.cit.com']])
    append_rows_to_coins(df1)
    # cursor.execute(f"USE {DB_NAME}")
    show_table('coins')


def test_add_rows_to_history():
    his = pd.DataFrame({'ID': [1,2], 'price': ['31', '32$'], 'market_cap':['300', '300$'], 
                        'snapped_at': [date.today(), date.today()], 'total_volume': ['11', '12$']})
    append_rows_to_history(his)
    show_table('history')
    return his


if __name__=='__main__':
    create_connection(DB_NAME)
    # his = test_add_rows_to_history()
#     test_add_rows()
        
# example_df = pd.DataFrame(['Bit', 600, 12000, 'www.bit.com'])


import pymysql

PASSWORD = input("Provide password for MySQL server:\n")

DB_NAME = 'crypto_currencies'


def create_connection(db_name=DB_NAME):
    """
    Creates and returns a connection and a cursor
    @param db_name: name of the database
    """
    cnx2 = pymysql.connect(host='localhost',
                           user='root',
                           password=PASSWORD,
                           database=db_name)
    cursor2 = cnx2.cursor()
    return cnx2, cursor2


def create_database(cnx, cursor, name=DB_NAME):
    """
    Creates the database
    @param name: name of the database
    """
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {name}")
    cnx.commit()


def create_coins_table(cnx, cursor):
    """
    Creates the table 'coins' in the database
    @param cnx: connection
    @param cursor: cursor to execute queries
    """
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE IF NOT EXISTS coins
            (ID int NOT NULL PRIMARY KEY, coin varchar(45), price varchar(45),
            market_cap varchar(45), coin_url varchar(45))"""
    cursor.execute(query)
    cnx.commit()


def append_rows_to_coins(cnx, cursor, data):
    """
    Gets the data as a Pandas dataframe with columns:
    ['index', 'coin_name', 'price', 'market_cap', 'URL'].
    Inserts it into the 'coins' table
    @param cnx: connection
    @param cursor: cursor to execute queries
    @param data: Pandas dataframe
    """
    data = data.values.tolist()
    query = """REPLACE INTO coins (ID, coin, price, market_cap, coin_url)
               VALUES (%s, %s, %s, %s, %s)"""

    try:
        cursor.executemany(query, data)
        cnx.commit()
        print(f"{len(data)} rows were successfully uploaded to the coins table")
    except:
        print("Rows were not appended correctly to the coins table")


def create_history_table(cnx, cursor):
    """
    Creates the table 'history' in the database
    @param cnx: connection
    @param cursor: cursor to execute queries
    """
    cursor.execute(f"USE {DB_NAME}")
    query = """CREATE TABLE IF NOT EXISTS history
            (ID int, date varchar(45), price varchar(45),
            market_cap varchar(45), volume_of_flow varchar(45),
            FOREIGN KEY (ID) REFERENCES coins(ID))"""
    cursor.execute(query)
    cnx.commit()


def append_rows_to_history(cnx, cursor, data):
    """
    Gets the data as a Pandas dataframe with columns:
    ['snapped_at', 'price', 'market_cap', 'total_volume', 'coin_id'].
    Inserts it into the 'history' table
    @param cnx: connection
    @param cursor: cursor to execute queries
    @param data: Pandas dataframe
    """
    data = data.to_dict('records')
    query = """REPLACE INTO history (ID, price, market_cap, volume_of_flow, date)
               VALUES (%(coin_id)s, %(price)s, %(market_cap)s, %(total_volume)s, %(snapped_at)s)"""
    try:
        cursor.executemany(query, data)
        cnx.commit()
        print(f"{len(data)} rows were successfully uploaded to the history table")
    except:
        print("Rows were not appended correctly to the history table")


def show_tables(cnx, cursor):
    """
    Prints the tables inside the database
    @param cnx: connection
    @param cursor: cursor to execute queries
    """
    cursor.execute(f"USE {DB_NAME}")
    cursor.execute("SHOW TABLES")
    print(cursor.fetchall())


def show_table(cnx, cursor, table_name):
    """
    Prints the content of the table provided
    @param cnx: connection
    @param cursor: cursor to execute queries
    @param table_name: table provided from the database
    """
    cursor.execute(f"SELECT * FROM {table_name}")
    print(f"content of {table_name}")
    print(cursor.fetchall())


def close_connection(cnx, cursor):
    """
    Performs the commit and closes the connection
    @param cnx: connection
    @param cursor: cursor to execute queries
    """
    cnx.commit()
    cursor.close()


def init():
    """
    Initializes by creating the database and the tables
    @return: the connection and the cursor
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
    """
    Main function of the module:
    - receives two dataframes,
    - fills empty cells with the above value
    @param df: main dataframe of the coins
    @param df_hist: dataframe with historical values of the coins
    """
    cnx, cursor = init()
    df_hist.fillna(method='ffill', inplace=True)
    append_rows_to_coins(cnx, cursor, df)
    append_rows_to_history(cnx, cursor, df_hist)
    close_connection(cnx, cursor)

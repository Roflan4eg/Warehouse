import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

mydb = pymysql.connections.Connection(
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    )

my_cursor = mydb.cursor()


my_cursor.execute(f'CREATE DATABASE {os.getenv("DB_NAME")}')
for db in my_cursor:
    print(db)

my_cursor.close()
mydb.close()
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='',
            database='blog_site'
        )
        if connection.is_connected():
            print("Connected to the MySQL database")
            return connection
    except Error as e:
        print(f"Error connecting to the database: {e}")
        return None

db_connection = create_connection()

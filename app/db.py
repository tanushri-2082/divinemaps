# app/db.py

import mysql.connector
from mysql.connector import Error

def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database="trialdivinemaps",
            autocommit=True
        )
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        raise
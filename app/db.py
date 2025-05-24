# app/db.py

import mysql.connector

def get_connection():
    """
    Return a new MySQL connection using local divinemaps database.
    Make sure you’ve replaced the user/password with your own.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",               # your MySQL username
        password="root",           # your MySQL password
        database="divinemaps"      # your database name
    )

# app/db.py

import mysql.connector

def get_connection():
    """
    Create and return a new MySQL‐connector connection.
    Make sure MySQL is running locally and that the credentials
    match your `trialdivinemaps` database setup.
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",               # MySQL username
        password="root",           # MySQL password
        database="trialdivinemaps" # database name
    )

# app/db.py

import mysql.connector

def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",               # MySQL username
        password="root",           # MySQL password
        database="trialdivinemaps"      # database name
    )

# app/db.py

import mysql.connector

def get_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",               # your MySQL username
        password="root",           # your MySQL password
        database="trialdivinemaps"      # your database name
    )

# app/db.py
import os
from mysql.connector import connect, Error

def get_connection():
    return connect(
        host     = 'localhost',
        user     = 'root',
        password = 'root',
        database = 'divinemaps',
        charset  = 'utf8mb4',
        autocommit=False,
    )
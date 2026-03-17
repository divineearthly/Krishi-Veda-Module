
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../krishi_veda_offline.db")

def get_connection():
    return sqlite3.connect(DB_PATH)

if __name__ == "__main__":
    # For standalone init testing
    pass

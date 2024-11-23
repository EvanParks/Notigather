from Database_interface import IDatabase
import sqlite3
import os

class Database(IDatabase):
    def __init__(self):
        self.database = 'NotiGather.db'
        self.connection = None

    def is_db_created(self):
        return os.path.exists(self.database)

    def create_database(self):
        conn = sqlite3.connect(self.database)
        
        cursor = conn.cursor()

        print("here")

        try:
            cursor.execute('''
            CREATE TABLE user_credentials (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                email TEXT NOT NULL,
                token TEXT
            )
            ''')
            print("Table user_credentials created successfully.")

            cursor.execute('''
            CREATE TABLE Gmail (
                user_id INTEGER,
                client_id TEXT,
                client_secret TEXT,
                access_token TEXT,
                refresh_token TEXT,
                token_expiry TIMESTAMP,
                token_uri TEXT,
                FOREIGN KEY(user_id) REFERENCES user_credentials(id)
            )
            ''')
            print("Table Gmail created successfully.")

            cursor.execute('''
            CREATE TABLE Slack (
                user_id INTEGER,
                access_token TEXT,
                FOREIGN KEY(user_id) REFERENCES user_credentials(id)
            )
            ''')
            print("Table Slack created successfully.")

            cursor.execute('''
            CREATE TABLE Outlook (
                user_id INTEGER,
                access_token TEXT,
                refresh_token TEXT,
                client_id TEXT,
                client_secret TEXT,
                token_expiry TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES user_credentials(id)
            )
            ''')
            print("Table Outlook created successfully.")

            conn.commit()
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
        finally:
            conn.close()

    def connect(self):
        if not self.is_db_created():
            self.create_database()
        
        self.connection = sqlite3.connect('NotiGather.db') 

    def execute_query(self, **kwargs):
        query = kwargs.get('query')
        parameters = kwargs.get('parameters')

        if self.connection == None:
            self.connect() 

        cursor = self.connection.cursor()

        if parameters:
            cursor.execute(query, parameters)
            result = cursor.fetchall()
        else:
            cursor.execute(query)
            result = cursor.fetchall() 
        
        self.connection.commit()
        return result 

    def close_database(self):
        if self.connection:
            self.connection.close()
            self.connection = None   
from Database_interface import IDatabase

class Database_orchestrator():
    def __init__(self, database: IDatabase):
        self.database = database

    def connect_database(self):
        self.database.connect()

    def execute_query(self, **kwargs):
        result = self.database.execute_query(**kwargs)

        return result

    def close_database(self):
        self.database.close_database() 
from Account_interface import IAccount

class Account(IAccount):
    def print_account(self):
        print("Account") 

    def create_user(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        email = kwargs.get('email')
        database = kwargs.get('database')

        query = "INSERT INTO user_credentials (username, password, email) VALUES (?, ?, ?)"
        parameters = (username, password, email)

        database.execute_query(query=query, parameters=parameters) 
        database.close_database()

    def check_user(self, **kwargs):
        username = kwargs.get('username')
        email = kwargs.get('email')
        database = kwargs.get('database')

        query = "SELECT count(*) FROM user_credentials WHERE username = ? or email = ?"
        parameters = (username, email)

        result = database.execute_query(query=query, parameters=parameters) 
        database.close_database()

        return result[0]

    def verify_user(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        database = kwargs.get('database')

        query = "SELECT count(*) FROM user_credentials WHERE username = ? AND password = ?"
        parameters = (username, password)

        result = database.execute_query(query=query, parameters=parameters) 
        database.close_database()

        return result[0]
    
    def check_email(self, **kwargs):
        email = kwargs.get('email')
        database = kwargs.get('database')

        query = "SELECT count(*) from user_credentials where email = ?"
        parameters = (email,)

        result = database.execute_query(query=query, parameters=parameters) 
        database.close_database()

        return result[0]
    
    def get_user_id(self, **kwargs):
        username = kwargs.get('username')
        password = kwargs.get('password')
        database = kwargs.get('database')

        query = "SELECT id FROM user_credentials WHERE username = ? AND password = ?"
        parameters = (username, password)

        result = database.execute_query(query=query, parameters=parameters) 
        database.close_database()

        if result:
            return result[0]
        else:
            return None
    
    def get_user_id_from_email(self, **kwargs):
        email = kwargs.get('email')
        database = kwargs.get('database')

        query = "SELECT id FROM user_credentials WHERE email = ?"
        parameters = (email,)

        result = database.execute_query(query=query, parameters=parameters) 
        database.close_database()

        if result:
            return result[0]
        else:
            return None
        
    def get_user_id_from_username(self, **kwargs):
        username = kwargs.get('username')
        database = kwargs.get('database')

        query = "SELECT id FROM user_credentials WHERE username = ?"
        parameters = (username,)

        result = database.execute_query(query=query, parameters=parameters) 
        database.close_database()

        if result:
            return result[0]
        else:
            return None
    
    def update_password(self, **kwargs): 
        user_id = kwargs.get('user_id')
        password = kwargs.get('password')
        token = kwargs.get('token')
        database = kwargs.get('database')

        result = self.check_token(user_id, token, database)

        if result:
            query = "UPDATE user_credentials SET password = ? WHERE id = ?"
            parameters = (password, user_id)

            database.execute_query(query=query, parameters=parameters)
            database.close_database()

            return True 
        else:
            return False 

    def check_token(self, user_id, token, database):
        query = "SELECT token FROM user_credentials WHERE id = ?"
        parameters = (user_id,)

        result = database.execute_query(query=query, parameters=parameters)
        database.close_database()

        if result:
            if token == result[0][0]:
                return True 

        return False  


        

   

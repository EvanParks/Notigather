from Token_interface import IToken

class Token_orchestrator():
    def __init__(self, token: IToken):
        self.token = token 

    def print_token(self):
        self.token.print_message() 

    def generate_access_token(self, **kwargs):
        token = self.token.generate_access_token(**kwargs) 

        return token 

    def generate_refresh_token(self, **kwargs):
        token = self.token.generate_refresh_token(**kwargs)

        return token 

    def isTokenValid(self, **kwargs):
        result = self.token.isTokenValid(**kwargs)

        return result 

    def isRefreshTokenValid(self, **kwargs):
        result = self.token.isRefreshTokenValid(**kwargs)

        return result 

    def get_user_id(self, **kwargs):
        user_id = self.token.get_user_id(**kwargs)

        return user_id 
    
    def decode(self, **kwargs):
        result = self.token.decode(**kwargs)

        return result 
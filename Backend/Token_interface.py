from abc import ABC, abstractmethod 

class IToken(ABC):
    @abstractmethod
    def print_message(self):
        pass 

    def generate_access_token(self):
        pass 

    def generate_refresh_token(self):
        pass 

    def isTokenValid(self):
        pass 

    def isRefreshTokenValid(self):
        pass 
    
    def get_user_id(self):
        pass 

    def decode(self):
        pass 
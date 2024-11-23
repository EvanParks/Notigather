from abc import ABC, abstractmethod 

class IAccount(ABC):
    @abstractmethod
    def print_account(self):
        pass 
    
    @abstractmethod
    def create_user(self):
        pass
    
    @abstractmethod
    def verify_user(self):
        pass 
    
    @abstractmethod
    def check_user(self):
        pass 
    
    @abstractmethod
    def check_email(self):
        pass 
    
    @abstractmethod
    def get_user_id(self):
        pass 
    
    @abstractmethod
    def get_user_id_from_email(self):
        pass 

    @abstractmethod
    def get_user_id_from_username(self):
        pass 

    @abstractmethod
    def update_password(self):
        pass 

from abc import ABC, abstractmethod 

class IService(ABC):
    @abstractmethod
    def print_message(self):
        pass 

    @abstractmethod
    def oauth(self):
        pass 
    
    @abstractmethod
    def oauthcallback(self):
        pass
    
    @abstractmethod
    def get_messages(self):
        pass 
    
    def mark_as_read(self):
        pass 

    

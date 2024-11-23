from abc import ABC, abstractmethod 

class IDatabase(ABC):
    @abstractmethod
    def is_db_created(self):
        pass 
    
    @abstractmethod
    def create_database(self):
        pass 
    
    @abstractmethod
    def connect(self):
        pass
    
    @abstractmethod
    def execute_query(self):
        pass 
    
    @abstractmethod
    def close_database(self):
        pass 
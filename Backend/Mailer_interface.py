from abc import ABC, abstractmethod 

class IMailer(ABC):
    @abstractmethod
    def print_mailer(self):
        pass 
    
    @abstractmethod
    def send_email(self):
        pass 

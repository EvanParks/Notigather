from Services_interface import IService 

class Service:
    def __init__(self, service: IService):
        self.service = service

    def print_message(self):
        self.service.print_message()

    def oauth(self, **kwargs):
        message = self.service.oauth(**kwargs)

        return message 

    def oauthcallback(self, **kwargs):
        self.service.oauthcallback(**kwargs)

    def get_messages(self, **kwargs):
        messages = self.service.get_messages(**kwargs)

        return messages 
    
    def mark_as_read(self, **kwargs):
        self.service.mark_as_read(**kwargs) 
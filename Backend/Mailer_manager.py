from Mailer_interface import IMailer

class Mailer_orchestrator():
    def __init__(self, mailer: IMailer):
        self.mailer = mailer    

    def print_mailer(self):
        self.mailer.print_mailer()  

    def send_email(self, **kwargs):
        self.mailer.send_email(**kwargs) 


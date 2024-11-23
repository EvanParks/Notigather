from Account_interface import IAccount

class Account_orchestrator():
    def __init__(self, account: IAccount):
        self.account = account 

    def print_account(self):
        self.account.print_account() 

    def create_user(self, **kwargs):
        self.account.create_user(**kwargs) 

    def verify_user(self, **kwargs):
        result = self.account.verify_user(**kwargs)

        return result[0] > 0 

    def check_user(self, **kwargs):
        result = self.account.check_user(**kwargs)

        return result[0] 
    
    def get_user_id(self, **kwargs):
        user_id = self.account.get_user_id(**kwargs)

        if user_id:
            return user_id[0]
        else:
            return user_id 
    
    def get_user_id_from_email(self, **kwargs):
        user_id = self.account.get_user_id_from_email(**kwargs)

        if user_id:
            return user_id[0]
        else:
            return user_id 
        
    def get_user_id_from_username(self, **kwargs):
        user_id = self.account.get_user_id_from_username(**kwargs)

        if user_id:
            return user_id[0]
        else:
            return user_id
    
    def update_password(self, **kwargs):
        message = self.account.update_password(**kwargs)

        return message 

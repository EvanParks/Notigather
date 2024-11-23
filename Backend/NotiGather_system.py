from Gmail_service import Gmail  
from Outlook_service import Outlook
from Slack_service import Slack 
from Service_operator import Service
from Account_manager import Account_orchestrator
from Token_manager import Token_orchestrator
from Account import Account
from Token import Token

from Database_manager import Database_orchestrator 
from Database import Database 

from Mailer_manager import Mailer_orchestrator 
from Mailer import Mailer

from operator import itemgetter 

class System:
    def __init__(self):
        gmail = Gmail() 
        self.gmail_service = Service(gmail)

        outlook = Outlook()
        self.outlook_service = Service(outlook)

        slack = Slack() 
        self.slack_service = Service(slack)

        account = Account()
        self.account_manager = Account_orchestrator(account)

        token = Token() 
        self.token_manager = Token_orchestrator(token)

        database = Database()
        self.database_manager = Database_orchestrator(database)

        mailer = Mailer()
        self.mailer_manager = Mailer_orchestrator(mailer)

    def get_gmail_message(self):
        self.gmail_service.print_message()

    def get_outlook_message(self):
        self.outlook_service.print_message()

    def get_slack_message(self):
        self.slack_service.print_message() 

    def get_account_message(self):
        self.account_manager.print_account() 

    def get_token_message(self):
        self.token_manager.print_token()

    def get_mailer_message(self):
        self.mailer_manager.print_mailer()

    def create_account(self, username, password, email):
        count = self.account_manager.check_user(username=username, email=email, database=self.database_manager)
        if count == 0:
            self.account_manager.create_user(username=username, password=password, email=email, database=self.database_manager)
            return {'message': True}
        else:
            return {'message' : False}

    def validate_account(self, username, password, app_secret, refresh_secret):
        result = self.account_manager.verify_user(username=username, password=password, database=self.database_manager)

        if result:
            user_id = self.account_manager.get_user_id(username=username, password=password, database=self.database_manager) 
            access_token = self.token_manager.generate_access_token(user_id=user_id,app_secret=app_secret, expiry=3600) 
            refresh_token = self.token_manager.generate_refresh_token(user_id=user_id,refresh_secret=refresh_secret, expiry=86400) 

            return {"message": result, "access_token": access_token, "refresh_token": refresh_token} 
        else:
            return {'message': result}
        
    def recover_account(self, email, recover_secret):
        user_id = self.account_manager.get_user_id_from_email(email=email, database=self.database_manager)

        if user_id != None:
            token = self.token_manager.generate_access_token(user_id=user_id, app_secret=recover_secret, expiry=3600)
            self.mailer_manager.send_email(email=email, token=token, user_id=user_id, database=self.database_manager)
            return {'message': True}
        else:
            return {'message' : False}
         
    def update_password(self, username, password, token, recover_secret):
        user_id = self.account_manager.get_user_id_from_username(username=username, database=self.database_manager)
        token_valid = self.token_manager.isTokenValid(app_secret=recover_secret, token=token)
        if token_valid:
            result = self.account_manager.update_password(user_id=user_id, password=password, token=token, database=self.database_manager)
        else:
            result = False 

        return {'message': result}   
        
    def gmail_oauth(self, CLIENT_SECRETS_FILE, access_token):
        authorization_url = self.gmail_service.oauth(CLIENT_SECRETS_FILE=CLIENT_SECRETS_FILE, access_token=access_token)

        return {'url': authorization_url}

    def gmail_oauthcallback(self, CLIENT_SECRETS_FILE, app_secret_key, authorization_response):
        self.gmail_service.oauthcallback(CLIENT_SECRETS_FILE=CLIENT_SECRETS_FILE, app_secret_key=app_secret_key, authorization_response=authorization_response, database_manager=self.database_manager, token_manager=self.token_manager) 

    def outlook_oauth(self, outlook_client_id, access_token, outlook_redirect_uri, outlook_scope):
        auth_url = self.outlook_service.oauth(outlook_client_id=outlook_client_id, access_token=access_token, outlook_redirect_uri=outlook_redirect_uri, outlook_scope=outlook_scope)

        return {'url': auth_url}
    
    def outlook_oauthcallback(self, outlook_client_id, outlook_client_secret, app_secret_key, outlook_redirect_uri, authorization_response):
        self.outlook_service.oauthcallback(outlook_client_id=outlook_client_id, outlook_client_secret=outlook_client_secret, outlook_redirect_uri=outlook_redirect_uri, authorization_response=authorization_response, database_manager=self.database_manager, app_secret_key=app_secret_key, token_manager=self.token_manager)

    def slack_oauth(self, access_token, slack_client_id, slack_redirect_url):
        auth_url = self.slack_service.oauth(access_token=access_token, slack_client_id=slack_client_id, slack_redirect_url=slack_redirect_url)

        return {'url': auth_url}
    
    def slack_oauthcallback(self, slack_client_id, slack_client_secret, app_secret_key, slack_redirect_uri, authorization_response):
        self.slack_service.oauthcallback(slack_client_id=slack_client_id, slack_client_secret=slack_client_secret, slack_redirect_uri=slack_redirect_uri, authorization_response=authorization_response, database_manager=self.database_manager, app_secret_key=app_secret_key, token_manager=self.token_manager)

    def get_messages(self, access_token, app_secret_key):
        user_id = self.token_manager.get_user_id(secret=app_secret_key, token=access_token)
        
        gmail_messages = self.gmail_service.get_messages(user_id=user_id, database_manager=self.database_manager)
        outlook_messages = self.outlook_service.get_messages(user_id=user_id, database_manager=self.database_manager)
        slack_messages = self.slack_service.get_messages(user_id=user_id, database_manager=self.database_manager)

        message_list = []
        message_list = message_list + gmail_messages + outlook_messages + slack_messages
        message_list.sort(key=itemgetter('time'), reverse=True)

        return message_list 
    
    def mark_as_read(self, access_token, app_secret_key, message_Id, source):
        user_id = self.token_manager.get_user_id(secret=app_secret_key, token=access_token) 

        if source == 'Google':
            self.gmail_service.mark_as_read(user_id=user_id, database_manager=self.database_manager, message_Id=message_Id)
        elif source == 'Outlook':
            self.outlook_service.mark_as_read(user_id=user_id, database_manager=self.database_manager, message_Id=message_Id)
        else:
            return {'Message': 'Invalid source'}
        
        return {'Message': 'Success'}
    
    def isTokenValid(self, secret, token):
        result = self.token_manager.isTokenValid(app_secret=secret, token=token)

        return result 
        
    def isRefreshTokenValid(self, secret, token):
        result = self.token_manager.isRefreshTokenValid(refresh_secret=secret, token=token)

        return result 
    
    def get_new_tokens(self, app_secret, refresh_secret, token):
        user_id = self.token_manager.get_user_id(secret=refresh_secret, token=token)
        access_token = self.token_manager.generate_access_token(user_id=user_id,app_secret=app_secret, expiry=3600)
        refresh_token = self.token_manager.generate_refresh_token(user_id=user_id,refresh_secret=refresh_secret, expiry=86400)

        return access_token, refresh_token
    
    def decode(self, app_secret, refresh_secret, access_token, refresh_token):
        self.token_manager.decode(secret=app_secret, token=access_token)
        self.token_manager.decode(secret=refresh_secret, token=refresh_token)


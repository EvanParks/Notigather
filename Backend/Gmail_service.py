from Services_interface import IService 
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import base64
from bs4 import BeautifulSoup
import re 
from urllib.parse import urlparse, parse_qs
from dateutil import parser
import requests
import datetime 

class Gmail(IService):
    def print_message(self):
        print("Gmail") 

    #Information for the Gmail OAuth process was pulled from https://developers.google.com/identity/protocols/oauth2/web-server#python. 
    def oauth(self, **kwargs):
        CLIENT_SECRETS_FILE=kwargs.get('CLIENT_SECRETS_FILE')
        access_token=kwargs.get('access_token')

        flow = self.google_flow(CLIENT_SECRETS_FILE)
        authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        state=access_token
        )

        return authorization_url

    #Information for the Gmail OAuth process was pulled from https://developers.google.com/identity/protocols/oauth2/web-server#python.
    def oauthcallback(self, **kwargs):
        CLIENT_SECRETS_FILE=kwargs.get('CLIENT_SECRETS_FILE')
        app_secret_key = kwargs.get('app_secret_key')
        authorization_response=kwargs.get('authorization_response')
        database_manager=kwargs.get('database_manager')
        token_manager = kwargs.get('token_manager')

        parsed_response = urlparse(authorization_response)
        code = parse_qs(parsed_response.query).get('code')
        state = parse_qs(parsed_response.query).get('state')[0]

        if token_manager.isTokenValid(app_secret=app_secret_key, token=state):
            flow = self.google_flow(CLIENT_SECRETS_FILE)
            if code != None: 
                flow.fetch_token(code=code[0])
                credentials = flow.credentials
                credentials_dict = self.credentials_to_dict(credentials)
                user_id = token_manager.get_user_id(secret=app_secret_key, token=state)
                self.add_credentials(credentials_dict, user_id, database_manager)
            else:
                print('No code')
        else:
            print('CSRF attack')

    #Information for using the google_auth_oauthlib.flow library was pulled from https://developers.google.com/identity/protocols/oauth2/web-server#python. 
    def google_flow(self, CLIENT_SECRETS_FILE):
        flow = Flow.from_client_secrets_file(
                CLIENT_SECRETS_FILE,
                scopes=['https://www.googleapis.com/auth/gmail.readonly', "https://www.googleapis.com/auth/gmail.modify"],
                redirect_uri='http://localhost:5000/oauth2callback'
            )
        
        return flow 
    
    def credentials_to_dict(self, credentials):
        return {
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'access_token': credentials.token,
            'refresh_token': credentials.refresh_token,
            'token_uri': credentials.token_uri
        }

    def add_credentials(self, credentials, user_id, database):
        user_id = int(user_id) 

        if self.check_user_id(user_id, database):
            query = "INSERT INTO Gmail (user_id) VALUES (?)"
            parameters = (user_id,)

            database.execute_query(query=query, parameters=parameters)

        for key, value in credentials.items():
            query = "UPDATE gmail SET {} = ? WHERE user_id = ?".format(key)
            parameters = (value, user_id) 

            database.execute_query(query=query, parameters=parameters)

        database.close_database()

    def get_messages(self, **kwargs):
        user_id = kwargs.get('user_id') 
        database = kwargs.get('database_manager')

        if user_id == None:
            return [] 
        if self.check_user_id(user_id, database):
            return []

        credentials = self.get_credentials(user_id, database)
        gmail_service = self.create_gmail_service(credentials)
        messages = self.list_messages(gmail_service, 5)

        return messages
    
    def check_user_id(self, user_id, database):
        user_id = int(user_id) 

        query = "SELECT COUNT(*) FROM Gmail where user_id = ?"
        parameters = (user_id,)

        result = database.execute_query(query=query, parameters=parameters)

        return result[0][0] == 0
    
    def get_credentials(self, user_id, database):
        query = "SELECT client_id, client_secret, access_token, refresh_token, token_uri from gmail where user_id = ?"
        parameters = (user_id,)

        result = database.execute_query(query=query, parameters=parameters)

        if result:
            return {
                'client_id': result[0][0],
                'client_secret': result[0][1],
                'access_token': result[0][2],
                'refresh_token': result[0][3],
                'token_uri': result[0][4] 
            }
        else:
            return None
    
    #Information for using the googleapiclient.discovery and google.oauth2.credentials libraries was pulled from https://developers.google.com/identity/protocols/oauth2/web-server#python.    
    def create_gmail_service(self, credentials):
        creds = Credentials(
            token=credentials['access_token'],
            refresh_token=credentials['refresh_token'],
            token_uri=credentials['token_uri'],
            client_id=credentials['client_id'],
            client_secret=credentials['client_secret']
        )
        gmail_service = build('gmail', 'v1', credentials=creds)
        return gmail_service

    #Information for sending a batch request to the Gmail API to receive messages was pulled from https://stackoverflow.com/questions/24439764/batch-fetching-messages-performance.   
    def list_messages(self, service, max_results):
        results = service.users().messages().list(userId='me', q="is:unread", maxResults=max_results).execute()
        message_ids = results.get('messages', [])
        messages = []

        batch = service.new_batch_http_request()

        for msg in message_ids:
            batch.add(service.users().messages().get(userId='me', id=msg['id']), callback=lambda request_id, response, exception: self.add(messages, request_id, response, exception))

        batch.execute()

        email_details = [self.extract_email(msg) for msg in messages if 'error' not in msg]

        return email_details
    
    #Information for sending a batch request to the Gmail API to receive messages was pulled from https://stackoverflow.com/questions/24439764/batch-fetching-messages-performance.
    def add(self, messages, request_id, response, exception):
        if exception is not None:
            messages.append({'id': request_id, 'error': str(exception)})
        else:
            messages.append(response)
    
    def extract_email(self, msg):
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])

        email_info = {} 
        email_info['attachments'] = []

        for header in headers:
            if header['name'] == 'Subject':
                email_info['subject'] = re.sub(r'["<>]', '', header['value'])
            if header['name'] == 'Date':
                time = parser.parse(re.sub(r'["<>]', '', header['value']))
                utc_time = time.astimezone(datetime.timezone.utc) 
                formatted_gmail_time = utc_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                email_info['time'] = formatted_gmail_time
            if header['name'] == 'From':
                if('<' in header['value'] or '>' in header['value']):
                    email_info['sender'], email_info['sender_email'] = header['value'].replace('"', '').replace('>', '').split("<")
                else:
                    email_info['sender'] = header['value']
            if header['name'] == 'To':
                email_info['receiver'] = re.sub(r'["<>]', '', header['value'])

        if 'parts' in payload:
            for part in payload['parts']:
                body_data = part['body'].get('data')
                if body_data:
                    decoded_body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                    if part['mimeType'] == 'text/html':
                        email_info['html_body'] = decoded_body
                        email_info['plain_body'] = self.extract_plain_text(decoded_body)
                    elif part['mimeType'] == 'text/plain':
                        email_info['plain_body'] = decoded_body
                
                if part.get('filename') and part.get('body') and part['body'].get('attachmentId'):
                    attachment_info = {
                        'filename': part['filename'],
                        'attachmentId': part['body']['attachmentId'],
                        'mimeType': part['mimeType']
                    }
                    email_info['attachments'].append(attachment_info)

        email_info['source'] = 'Google'
        email_info['messageId'] = msg.get('id')
        email_info['threadId'] = msg.get('threadId')

        return email_info 
    
    def extract_plain_text(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for tag in soup(['script', 'style', 'span']):
            tag.decompose()
        
        plain_text = soup.get_text(separator='\n', strip=True)
        
        return plain_text
    
    ##Information for marking a Gmail message as read was pulled from https://stackoverflow.com/questions/26510757/mark-as-read-mail-method.  
    def mark_as_read(self, **kwargs):
        user_id = kwargs.get('user_id')
        database = kwargs.get('database_manager')
        message_Id = kwargs.get('message_Id')

        credentials = self.get_credentials(user_id, database)
        gmail_service = self.create_gmail_service(credentials)

        try:
            gmail_service.users().messages().modify(userId='me', id=message_Id, body={'removeLabelIds': ['UNREAD']}).execute()
        except Exception as e:
            print(e)

    


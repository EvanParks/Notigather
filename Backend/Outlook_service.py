from Services_interface import IService 
import requests
from urllib.parse import urlparse, parse_qs
import time 
from dateutil import parser
import datetime 

class Outlook(IService):
    def print_message(self):
        print("Outlook") 
    
    #Information for the Outlook OAuth process was pulled from https://learn.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13 
    def oauth(self, **kwargs):
        outlook_client_id = kwargs.get('outlook_client_id')
        access_token = kwargs.get('access_token')
        outlook_redirect_uri = kwargs.get('outlook_redirect_uri') 
        outlook_scope = kwargs.get('outlook_scope').replace(' ', ',')
        auth_url = (
            f"https://login.microsoftonline.com/common/oauth2/v2.0/authorize?"
            f"client_id={outlook_client_id}&"
            f"response_type=code&"
            f"redirect_uri={outlook_redirect_uri}&"
            f"scope={outlook_scope}&"
            f"state={access_token}"
        ) 

        return auth_url 

    #Information for the Outlook OAuth process was pulled from https://learn.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13 
    def oauthcallback(self, **kwargs):
        outlook_client_id= kwargs.get('outlook_client_id')   
        outlook_client_secret= kwargs.get('outlook_client_secret')  
        outlook_redirect_uri= kwargs.get('outlook_redirect_uri') 
        authorization_response= kwargs.get('authorization_response') 
        database_manager= kwargs.get('database_manager')
        app_secret_key = kwargs.get('app_secret_key')
        token_manager= kwargs.get('token_manager')
 
        parsed_url = urlparse(authorization_response)
        code = parse_qs(parsed_url.query).get('code', [None])[0]
        state = parse_qs(parsed_url.query).get('state')[0]
        
        if token_manager.isTokenValid(app_secret=app_secret_key, token=state):
            if code != None: 
                token_url = f"https://login.microsoftonline.com/common/oauth2/v2.0/token"
                data = {
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': outlook_redirect_uri,
                    'client_id': outlook_client_id,
                    'client_secret': outlook_client_secret
                }

                response = requests.post(token_url, data=data)

                response_data = response.json()
                access_token = response_data.get('access_token')
                refresh_token = response_data.get('refresh_token')
                expiry_time = time.time() + response_data.get('expires_in')
                user_id = token_manager.get_user_id(secret=app_secret_key, token=state)

                self.add_credentials(access_token, user_id, refresh_token, expiry_time, outlook_client_id, outlook_client_secret, database_manager)
            else:
                print('No code')
        else:
            print('CSRF attack')

    def add_credentials(self, access_token, user_id, refresh_token, expiry_time, client_id, client_secret, database):
        user_id = int(user_id) 
        expiry_time = int(expiry_time)

        if self.check_user_id(user_id, database):
            query = "INSERT INTO Outlook (user_id) VALUES (?)"
            parameters = (user_id,)

            database.execute_query(query=query, parameters=parameters)

        query = "UPDATE Outlook SET access_token = ?, refresh_token = ?, expiry = ?, client_id = ?, client_secret = ? WHERE user_id = ?"
        parameters = (access_token, refresh_token, expiry_time, client_id, client_secret, user_id) 

        database.execute_query(query=query, parameters=parameters)

        database.close_database()

    def get_messages(self, **kwargs):
        user_id = kwargs.get('user_id') 
        database = kwargs.get('database_manager')

        if user_id == None:
            return []
        if self.check_user_id(user_id, database):
            return []

        result = self.get_credentials(user_id, database) 
        access_token, refresh_token, expiry, client_secret, client_id = result 
        curr_time = time.time()

        if (curr_time >= expiry):
            self.refresh_token(refresh_token, client_secret, client_id, user_id, database)
            result = self.get_credentials(user_id, database) 
            access_token, refresh_token, expiry, client_secret, client_id = result 
        
        messages = self.get_user_emails(access_token, 5)

        return messages   

    def check_user_id(self, user_id, database):
        user_id = int(user_id) 

        query = "SELECT COUNT(*) FROM Outlook where user_id = ?"
        parameters = (user_id,)

        result = database.execute_query(query=query, parameters=parameters)

        return result[0][0] == 0 
    
    def get_credentials(self, user_id, database):
        user_id = int(user_id)

        query = "SELECT access_token, refresh_token, expiry, client_secret, client_id from outlook where user_id = ?"
        parameters = (user_id,)

        result = database.execute_query(query=query, parameters=parameters)
        database.close_database()

        if result:
            return result[0][0], result[0][1], result[0][2], result[0][3], result[0][4]
        else:
            return None 
    
    #Information for getting Outlook messages was pulled from https://learn.microsoft.com/en-us/graph/api/user-list-messages?view=graph-rest-1.0&tabs=http.  
    def get_user_emails(self, access_token, max_results):    
        url = 'https://graph.microsoft.com/v1.0/me/messages'
        params = {
            '$top': max_results,
            '$filter': 'isRead eq false',
            '$select': 'receivedDateTime,from,toRecipients,subject,body,conversationId, WebLink'
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers, params=params)

        emails = response.json().get('value', [])

        email_details = []
        for email in emails:
            content_type = email.get('body', {}).get('contentType', 'text')
            body_content = email.get('body', {}).get('content', '')

            address_list, to_recipients = [], email.get('toRecipients', [])
            for recipient in to_recipients:
                address = recipient.get('emailAddress', {}).get('address', '')
                address_list.append(address)

            recipients = ", ".join(address_list)

            time = parser.parse(email.get('receivedDateTime'))
            utc_time = time.astimezone(datetime.timezone.utc) 
            formatted_outlook_time = utc_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

            details = {
                'subject': email.get('subject'),
                'time': formatted_outlook_time,
                'sender': email.get('from', {}).get('emailAddress', {}).get('name'),
                'sender_email': email.get('from', {}).get('emailAddress', {}).get('address'), 
                'receiver': recipients
            }

            if content_type == 'html':
                details['html_body'] = body_content
            else:
                details['plain_body'] = body_content

            details['source'] = 'Outlook'
            details['messageId'] = email.get('id')
            details['threadId'] = email.get('conversationId')
            details['webLink'] = email.get('webLink')

            email_details.append(details)

        return email_details 
    
    #Information for refreshing an Outlook access token was pulled from https://learn.microsoft.com/en-us/advertising/guides/authentication-oauth-get-tokens?view=bingads-13   
    def refresh_token(self, refresh_token, client_secret, client_id, user_id, database):
        token_url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"

        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
            'client_id': client_id,
            'client_secret': client_secret,
        }

        response = requests.post(token_url, data=data)
        response_data = response.json()

        access_token = response_data['access_token']
        refresh_token = response_data['refresh_token']
        expiry = time.time() + response_data['expires_in']

        self.update_credentials(access_token, refresh_token, expiry, user_id, database) 

    def update_credentials(self, access_token, refresh_token, expiry_time, user_id, database):
        user_id = int(user_id) 

        query = "UPDATE Outlook SET access_token = ?, refresh_token = ?, expiry = ? WHERE user_id = ?"
        parameters = (access_token, refresh_token, expiry_time, user_id) 

        database.execute_query(query=query, parameters=parameters)

        database.close_database()
    
    #Information for marking an Outlook message as read was pulled from https://learn.microsoft.com/en-us/graph/api/message-update?view=graph-rest-1.0&tabs=http.  
    def mark_as_read(self, **kwargs):
        user_id = kwargs.get('user_id') 
        database = kwargs.get('database_manager')
        message_Id = kwargs.get('message_Id')

        result = self.get_credentials(user_id, database) 
        access_token, refresh_token, expiry, client_secret, client_id = result

        url = f'https://graph.microsoft.com/v1.0/me/messages/{message_Id}'
        data = {
            'isRead': True
        }
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }

        try:
            requests.patch(url, headers=headers, json=data)
        except Exception as e:
            print(e)
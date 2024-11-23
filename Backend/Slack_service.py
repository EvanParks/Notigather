from Services_interface import IService 
import requests
from urllib.parse import urlparse, parse_qs
import re 
import datetime 
from operator import itemgetter

class Slack(IService):
    def print_message(self):
        print("Slack") 

    #Information for the Slack OAuth process was pulled from https://api.slack.com/authentication/oauth-v2. 
    def oauth(self, **kwargs):
        access_token = kwargs.get('access_token')
        client_id = kwargs.get('slack_client_id')
        redirect_url = kwargs.get('slack_redirect_url')
        auth_url = (
            f"https://slack.com/oauth/v2/authorize?"
            f"client_id={client_id}&"
            f"scope=channels:history,groups:history,im:history,mpim:history,channels:read,groups:read,im:read,mpim:read&"
            f"user_scope=channels:history,groups:history,im:history,mpim:history,channels:read,groups:read,im:read,mpim:read,users.profile:read,users:read,users:read.email&"
            f"redirect_uri={redirect_url}&"
            f"state={access_token}"
        )
        
        return auth_url

    #Information for the Slack OAuth process was pulled from https://api.slack.com/authentication/oauth-v2.
    def oauthcallback(self, **kwargs):
        client_id = kwargs.get('slack_client_id') 
        client_secret = kwargs.get('slack_client_secret') 
        redirect_url = kwargs.get('slack_redirect_url')
        authorization_response = kwargs.get('authorization_response') 
        database_manager = kwargs.get('database_manager')
        app_secret_key = kwargs.get('app_secret_key')
        token_manager= kwargs.get('token_manager')

        parsed_url = urlparse(authorization_response)
        code = parse_qs(parsed_url.query).get('code', [None])[0]
        state = parse_qs(parsed_url.query).get('state')[0]

        if token_manager.isTokenValid(app_secret=app_secret_key, token=state):
            if code != None:

                token_url = "https://slack.com/api/oauth.v2.access"
                payload = {
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "code": code,
                    "redirect_uri": redirect_url
                }

                response = requests.post(token_url, data=payload)
                response_data = response.json()
                access_token = response_data.get('authed_user', {}).get('access_token')
                user_id = token_manager.get_user_id(secret=app_secret_key, token=state)
                self.add_credentials(user_id, access_token, database_manager)
            else:
                print('No code') 
        else:
            print('CSRF attack')

    def add_credentials(self, user_id, access_token, database):
        user_id = int(user_id) 

        if self.check_user_id(user_id, database):
            query = "INSERT INTO Slack (user_id) VALUES (?)"
            parameters = (user_id,)

            database.execute_query(query=query, parameters=parameters)

        query = "UPDATE Slack SET access_token = ? WHERE user_id = ?"
        parameters = (access_token, user_id) 

        database.execute_query(query=query, parameters=parameters)
        database.close_database()

    def check_user_id(self, user_id, database):
        user_id = int(user_id) 

        query = "SELECT COUNT(*) FROM Slack where user_id = ?"
        parameters = (user_id,)

        result = database.execute_query(query=query, parameters=parameters)

        return result[0][0] == 0

    def get_messages(self, **kwargs):
        user_id=kwargs.get('user_id') 
        database=kwargs.get('database_manager')

        access_token = self.get_credentials(user_id, database)
        result = self.get_token_info(access_token)
        user = result.get('user_id')
        conversation_ids = self.get_all_conversations(access_token)
        messages = []

        for conversation in conversation_ids:
            conversation_name = conversation.get('name')
            conversation_id = conversation.get('id') 
            conversation_messages = self.get_conversation_messages(access_token, conversation_id)

            for message in conversation_messages:
                if message.get('user') != user:
                    if message.get('thread_ts'):
                        replies = self.get_thread(access_token, conversation_id, message.get('thread_ts'))
                        
                        for reply in replies:
                            if reply.get('user') != user:
                                messages.append(self.process_message(access_token, reply, conversation_id, conversation_name))
                    else:
                        messages.append(self.process_message(access_token, message, conversation_id, conversation_name))
        
        finalized_messages = self.sort_and_limit_messages(messages, 5)

        return finalized_messages 
    
    def get_credentials(self, user_id, database):
        user_id = int(user_id)

        query = "SELECT access_token from Slack where user_id = ?"
        parameters = (user_id,)

        result = database.execute_query(query=query, parameters=parameters)
        database.close_database()

        if result:
            return result[0][0] 
        else:
            return None  
        
    def sort_and_limit_messages(self, messages, limit):
        messages.sort(key=itemgetter('time'), reverse=True)

        limited_messages = messages[:limit]

        return limited_messages  

    def process_message(self, access_token, message, conversation_id, conversation_name):
        link = self.get_link(access_token, conversation_id, message.get('ts'))

        response = self.get_user_info(access_token, message.get("user"))

        if message.get('subtype') == 'channel_join' or conversation_id.startswith('C'):
            text = self.replace_userid(message.get('text'), message.get('user'), response['username'])
            receiver = 'All members'
        else:
            text = message.get('text')
            result = self.get_members(access_token, conversation_id)
            filtered_ids = [user_id for user_id in result if user_id != message.get('user')]

            receivers = []
            for id in filtered_ids:
                user_id_response = self.get_user_info(access_token, id)
                receivers.append(user_id_response['username'])

            receiver = ", ".join(receivers) 

        if conversation_name == None:
            conversation_name = "Direct Message"

        timestamp_seconds = datetime.datetime.utcfromtimestamp(float(message.get("ts")))
        formatted_time = timestamp_seconds.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        return {
            "subject": "#" + conversation_name,  
            "time": formatted_time,  
            "sender": response["username"],
            "sender_email" : response["email"],    
            "receiver": receiver, 
            "plain_body" : text,
            "source": "Slack",
            "messageId": message.get("client_msg_id", ""),  
            "threadID": message.get("thread_ts", ""),
            "webLink": link
        } 
    
    def replace_userid(self, message_text, user_id, actual_username):
        pattern = r"<@{}>".format(user_id)
    
        updated_body = re.sub(pattern, actual_username, message_text)
    
        return updated_body

    #Information for the Slack conversations.list API method was pulled from https://api.slack.com/methods/conversations.list. 
    def get_all_conversations(self, access_token):
        url = "https://slack.com/api/conversations.list"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "limit": 100,
            "types": "public_channel,private_channel,mpim,im"
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()
    
        if data.get("ok"):
            conversations = data.get("channels", [])
            return conversations
        else:
            print(f"Error fetching channels: {data.get('error')}")
            return []
    
    #Information for the Slack conversations.history API method was pulled from https://api.slack.com/methods/conversations.history.
    def get_conversation_messages(self, access_token, conversation_id):
        url = "https://slack.com/api/conversations.history"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "channel": conversation_id,
            "limit": 5 
        }
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data.get("ok"):
            messages = data.get("messages", [])
            return messages
        else:
            print(f"Error fetching messages: {data.get('error')}")

        return []

    #Information for the Slack auth.test API method was pulled from https://api.slack.com/methods/auth.test. 
    def get_token_info(self, access_token):
        url = "https://slack.com/api/auth.test"
        headers = {
        "Authorization": f"Bearer {access_token}"
        }
    
        response = requests.post(url, headers=headers)
    
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error fetching user info: {response.status_code} - {response.text}")
            return None
    
    #Information for the Slack users.info API method was pulled from https://api.slack.com/methods/users.info.
    def get_user_info(self, access_token, user_id):
        url = f"https://slack.com/api/users.info?user={user_id}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(url, headers=headers)
        data = response.json()
        
        if response.status_code == 200:
            username = data['user'].get('name')
            email = data['user'].get('profile', {}).get('email')

            return {
                'username' : username,
                'email' : email
            }
        else:
            print(f"Error fetching user info: {response.status_code} - {response.text}")
            return None
        
    #Information for the Slack conversations.members API method was pulled from https://api.slack.com/methods/conversations.members.   
    def get_members(self, access_token, id):
        url = f"https://slack.com/api/conversations.members?channel={id}"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.get(url, headers=headers)
        data = response.json()

        if data.get("ok"):
            return data.get("members", [])
        else:
            print(f"Error fetching members: {data.get('error')}")
            return []
        
    #Information for the Slack chat.getPermalink API method was pulled from https://api.slack.com/methods/chat.getPermalink. 
    def get_link(self, access_token, conversation_id, message_ts):
        url = "https://slack.com/api/chat.getPermalink"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "channel": conversation_id,
            "message_ts": message_ts
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        
        if data.get("ok"):
            return data["permalink"]
        else:
            print(f"Error fetching permalink: {data.get('error')}")
            return None
    
    #Information for the Slack conversations.replies API method was pulled from https://api.slack.com/methods/conversations.replies. 
    def get_thread(self, access_token, conversation_id, thread_ts):
        url = "https://slack.com/api/conversations.replies"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        params = {
            "channel": conversation_id,
            "ts": thread_ts
        }
        
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if data.get("ok"):
            return data.get("messages", [])
        else:
            print(f"Error fetching thread messages: {data.get('error')}")
            return [] 



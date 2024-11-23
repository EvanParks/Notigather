from Token_interface import IToken 
import jwt 
import datetime 

class Token(IToken):
    def print_message(self):
        print("Token") 

    #Information for generating a JWT token was pulled from https://pyjwt.readthedocs.io/en/stable/usage.html#encoding-decoding-tokens-with-hs256. 
    def generate_access_token(self, **kwargs):
        user_id = kwargs.get('user_id')
        app_secret = kwargs.get('app_secret')
        expiry = kwargs.get('expiry')

        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        token = jwt.encode(payload, app_secret, algorithm='HS256')
        return token 

    #Information for generating a JWT token was pulled from https://pyjwt.readthedocs.io/en/stable/usage.html#encoding-decoding-tokens-with-hs256. 
    def generate_refresh_token(self, **kwargs):
        user_id = kwargs.get('user_id')
        refresh_secret = kwargs.get('refresh_secret')
        expiry = kwargs.get('expiry')

        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=expiry),
            'iat': datetime.datetime.utcnow(),
            'sub': user_id
        }
        token = jwt.encode(payload, refresh_secret, algorithm='HS256')
        return token 

    #Information for decoding a JWT token was pulled from https://pyjwt.readthedocs.io/en/latest/api.html.
    def isTokenValid(self, **kwargs):
        app_secret = kwargs.get('app_secret')
        token = kwargs.get('token')

        try:
            jwt.decode(token, app_secret, algorithms=['HS256'])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
    
    #Information for decoding a JWT token was pulled from https://pyjwt.readthedocs.io/en/latest/api.html.
    def isRefreshTokenValid(self, **kwargs):
        refresh_secret = kwargs.get('refresh_secret')
        token = kwargs.get('token')

        try:
            jwt.decode(token, refresh_secret, algorithms=['HS256'])
            return True
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False

    def get_user_id(self, **kwargs):
        secret = kwargs.get('secret')
        token = kwargs.get('token')

        try:
            payload = jwt.decode(token, secret, algorithms=['HS256'])
            return payload['sub']
        except jwt.InvalidTokenError:
            return None
        
    def decode(self, **kwargs):
        secret = kwargs.get('secret')
        token = kwargs.get('token')
        
        payload = jwt.decode(token, secret, algorithms=['HS256'])

        return payload 



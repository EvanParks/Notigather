from flask import Flask, redirect, request, jsonify, make_response
from flask_cors import CORS
import os
from dotenv import load_dotenv 
from NotiGather_system import System

load_dotenv() 
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.getenv('app_secret_key') 
app_refresh_key = os.getenv('app_refresh_key')
recover_secret_key = os.getenv('recover_secret_key') 
CLIENT_SECRETS_FILE = os.getenv('CLIENT_SECRETS_FILE')
slack_client_id = os.getenv('slack_client_id')
slack_client_secret = os.getenv('slack_client_secret')
slack_redirect_url = os.getenv('slack_redirect_url') 
outlook_client_id = os.getenv('outlook_client_id')
outlook_client_secret = os.getenv('outlook_client_secret')
outlook_redirect_uri = os.getenv('outlook_redirect_uri')
outlook_scope = os.getenv('outlook_scope')

@app.route('/register', methods=['POST'])
def register():
    notigather = System()

    data = request.json
    if 'username' in data and 'password' in data and 'email' in data:
        message = notigather.create_account(data['username'], data['password'], data['email'])
        return jsonify(message)
    
    return jsonify({'error': 'Missing username or password or email'}), 400

@app.route('/verify', methods=['POST'])
def verify():
    notigather = System()

    data = request.json
    if 'username' in data and 'password' in data:
        result = notigather.validate_account(data['username'], data['password'], app.secret_key, app_refresh_key)
        access_token = result.get('access_token')
        refresh_token = result.get('refresh_token')

        response = make_response()

        response = {
            'message': result['message']
        }

        response = make_response(response)

        if access_token and refresh_token:
            response.set_cookie('access_token', access_token, httponly=True, secure=True, samesite='None', path='/')
            response.set_cookie('refresh_token', refresh_token, httponly=True, secure=True, samesite='None', path='/')
        
        return response
    
    return jsonify({'error': 'Missing username or password or email'}), 400

@app.route('/account_recovery', methods=['POST'])
def account_recovery():
    notigather = System()
    
    data = request.json 
   
    if 'email' in data:
        message = notigather.recover_account(data['email'], recover_secret_key)
        return jsonify(message)
    
    return jsonify({'error': 'Missing email'}), 400 

@app.route('/update_password', methods=['POST'])
def update_password():
    notigather = System() 

    data = request.json

    if 'username' in data and 'newPassword' and 'token' in data:
        message = notigather.update_password(data['username'], data['newPassword'], data['token'], recover_secret_key)
        return jsonify(message) 
    else:
        return jsonify({'error': 'Missing username, password, or token'}), 400 

#Google
@app.route('/oauth2call', methods=['GET', 'POST'])
def oauth2call():
    notigather = System()
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token') 

    if access_token and refresh_token:
        access_result = notigather.isTokenValid(app.secret_key, access_token)
        refresh_result = notigather.isRefreshTokenValid(app_refresh_key, refresh_token)
        if access_result:
            message = notigather.gmail_oauth(CLIENT_SECRETS_FILE, access_token)
            message['token_status'] = ''
        elif not access_result and refresh_result:
            message = {'token_status': 'Refresh'}
        else:
            message = {'token_status': 'Logout'}

        return jsonify(message)
    else:
        return jsonify({'error': 'Invalid token'}), 401

#Google
@app.route('/oauth2callback', methods=['GET'])
def oauth2callback():
    notigather = System()

    notigather.gmail_oauthcallback(CLIENT_SECRETS_FILE, app.secret_key, authorization_response=request.url)

    return redirect('http://localhost:3000/dashboard')

@app.route('/outlookoauth2call', methods=['GET'])
def outlookoauth2call():
    notigather = System()
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token') 

    if access_token and refresh_token:
        access_result = notigather.isTokenValid(app.secret_key, access_token)
        refresh_result = notigather.isRefreshTokenValid(app_refresh_key, refresh_token)
        if access_result:
            message = notigather.outlook_oauth(outlook_client_id, access_token, outlook_redirect_uri, outlook_scope)
            message['token_status'] = ''
        elif not access_result and refresh_result:
            message = {'token_status': 'Refresh'}
        else:
            message = {'token_status': 'Logout'}
    
        return jsonify(message)
    else:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/outlookoauth2callback', methods=['GET', 'POST'])
def outlookoauth2callback():
    notigather = System()

    notigather.outlook_oauthcallback(outlook_client_id, outlook_client_secret, app.secret_key, outlook_redirect_uri, authorization_response=request.url)

    return redirect('http://localhost:3000/dashboard') 

#Slack
@app.route('/slackoauth2call', methods=['GET', 'POST'])
def slackoauth2call():
    notigather = System()
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token') 

    if access_token and refresh_token:
        access_result = notigather.isTokenValid(app.secret_key, access_token)
        refresh_result = notigather.isRefreshTokenValid(app_refresh_key, refresh_token)
        if access_result:
            message = notigather.slack_oauth(access_token, slack_client_id, slack_redirect_url)
            message['token_status'] = ''
        elif not access_result and refresh_result:
            message = {'token_status': 'Refresh'}
        else:
            message = {'token_status': 'Logout'}
    
        return jsonify(message)
    else:
        return jsonify({'error': 'Invalid token'}), 401

#Slack
@app.route('/slackoauth2callback', methods=['GET'])
def slackoauth2callback():
    notigather = System()

    notigather.slack_oauthcallback(slack_client_id, slack_client_secret, app.secret_key, slack_redirect_url, authorization_response=request.url)

    return redirect('http://localhost:3000/dashboard')

@app.route('/get_messages', methods=['GET', 'POST'])
def get_messages():
    notigather = System()
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token') 

    if access_token and refresh_token:
        access_result = notigather.isTokenValid(app.secret_key, access_token)
        refresh_result = notigather.isRefreshTokenValid(app_refresh_key, refresh_token)
        if access_result:
            messages = notigather.get_messages(access_token, app.secret_key)
        elif not access_result and refresh_result:
            messages = {'token_status': 'Refresh'}
        else:
            messages = {'token_status': 'Logout'}
    
        return jsonify(messages)
    else:
        return jsonify({'error': 'Invalid token'}), 401

@app.route('/mark_as_read', methods=['GET', 'POST'])
def mark_as_read():
    notigather = System()
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token') 
    data = request.json

    if access_token and refresh_token:
        access_result = notigather.isTokenValid(app.secret_key, access_token)
        refresh_result = notigather.isRefreshTokenValid(app_refresh_key, refresh_token)
        if access_result:
           message = notigather.mark_as_read(access_token, app.secret_key, data['message_Id'], data['source'])
           message['token_status'] = ''
        elif not access_result and refresh_result:
            message = {'token_status': 'Refresh'}
        else:
            message = {'token_status': 'Logout'}
    
        return jsonify(message)
    else:
        return jsonify({'error': 'Invalid token'}), 401
    
@app.route('/get_new_tokens', methods=['POST'])
def get_new_tokens():
    notigather = System()
    access_token = request.cookies.get('access_token')
    refresh_token = request.cookies.get('refresh_token') 

    if access_token and refresh_token:
        refresh_result = notigather.isRefreshTokenValid(app_refresh_key, refresh_token)
        if refresh_result:
            new_access_token, new_refresh_token = notigather.get_new_tokens(app.secret_key, app_refresh_key, refresh_token)
            response = make_response(jsonify({'token_status': 'Refreshed'}))
            response.set_cookie('access_token', new_access_token, httponly=True, secure=True, samesite='None', path='/')
            response.set_cookie('refresh_token', new_refresh_token, httponly=True, secure=True, samesite='None', path='/')
            #notigather.decode(app.secret_key, app_refresh_key, new_access_token, new_refresh_token)
            
            return response
        else:
            message = {'token_status': 'Logout'}

        return jsonify(message) 
    else:
        return jsonify({'error': 'No tokens'}), 401
    
@app.route('/signout', methods=['POST'])
def signout():
    response = make_response(jsonify({"message": "Successfully signed out."}), 200)
    response.set_cookie('access_token', '', expires=0, httponly=True, secure=True, samesite='None', path='/')
    response.set_cookie('refresh_token', '', expires=0, httponly=True, secure=True, samesite='None', path='/')

    return response 

if __name__ == '__main__':
    #notigather = System()
    #notigather.get_gmail_message() 
    #notigather.get_outlook_message()
    #notigather.get_slack_message() 
    #notigather.get_token_message()
    #notigather.get_account_message()
    #print(notigather.create_account('Evan', 'Evan', 'EvanGParks@gmail.com'))
    #print(notigather.validate_account('Evan', 'Evan')) 
    #print(notigather.recover_account('EvanGParks@gmail.com'))
    #print(notigather.gmail_oauth(CLIENT_SECRETS_FILE))
    #print(notigather.get_messages(1))
    #print(notigather.outlook_oauth(outlook_client_id, outlook_redirect_uri, outlook_scope))
    #notigather.get_mailer_message()
    #print(notigather.recover_account('EvanGParks@gmail.com'))
    #print(notigather.recover_account('FakeEmail@gmail.com'))
    app.run(debug=True)






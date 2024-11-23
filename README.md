# NotiGather
Notigather is a web application that intends to improve productivity by eliminating the need to track incoming messages across multiple platforms. The objective of Notigather is accomplished through integrating with a multitude of messaging services such as Gmail, Outlook, and Slack and allowing users to view all their messages within a single, centralized dashboard.

## Background
The motivation to create Notigather stemmed from the demands of my current employment, which requires managing a substantial number of clients and requests. Due to the number of requests that need to be handled each day, there is an incessant need to communicate with clients and colleagues across several messaging platforms. As a result, I desired a tool that would help me effectively track my work notifications and reduce the time spent managing messages from different services. Additionally, I was introduced to web development in my Cloud Application Development course that I took this last winter semester. This course spurred my interest in web development, and I decided that this project would offer me an opportunity to expand on my interest and increase my experience and knowledge with new technologies. 

## Features
- Offers processes for account creation, account authentication, and account recovery.
- Implements added security through the use of cookies. 
- Enables users to easily complete the required OAuth flow for Gmail, Outlook, and Slack.  
- Gathers notifications from enabled services and displays them for user interaction.
- Automatically handles the refresh of user cookies, message retrieval, and service access tokens.  
- Offers functionality for expanding and collapsing messages. 
- Allows users to mark Gmail and Outlook messages as read. 
- Provides users with the ability to filter messages by desired services. 
- Enables users to easily open messages within the service of origin. 

## Built with
- Backend: Flask
- Frontend: React 

# Getting Started
## Prerequisites 
Setup ngrok
1. Create a free Ngrok account
2. Claim a free static domain 
3. Copy and save the domain

Create the Notigather application within the Google Cloud Platform, Azure, and Slack portal. 
- Google Cloud Platform: 
1. Navigate to https://console.cloud.google.com  
2. Go to the API's & Services page and click the OAuth consent screen tab
3. Create a new application with the title Notigather, add the redirect http://localhost:5000/oauth2callback, add Gmail scopes auth/gmail.modify and auth/gmail.readonly, and add an email for test users.   
4. Create OAuth client ID credentials for a web application. 
5. Save the credentials
- Azure: 
1. Navigate to https://portal.azure.com
2. Go to App registrations 
3. Create a new application with the title Notigather add the redirect http://localhost:5000/outlookoauth2callback, add scopes Mail.Read, Mail.ReadWrite, offline_access, and User.Read.  
4. Within the Certificates and secrets, create credentials for the application. 
5. Save the credentials 
- Slack:
1. Navigate to https://api.slack.com
2. Go to Your Apps
3. Create a new application with the title Notigather, add the ngrok domain as the redirect, and add user scopes channels:history, channels:read, groups:history, groups:read im:history, im:read, mpim:history, mpim:read, users:read, users.profile:read, and users:read.email.   
4. Install the app to a workspace 
5. Save the credentials
## Setup
1. Rename the .env example file to .env
2. Add values collected from each service to the .env file  

## Installation 
- Install Python ```https://www.python.org/downloads/```  
- Install Node.js ```https://nodejs.org/en``` 
- Install dependencies for backend ```pip install -r requirements.txt``` 
- Install Dependencies for frontend ```npm install```  
- Run Flask server ```python Flaskapp.py```
- Run npm server ```npm start```
- Run ngrok ```ngrok http --hostname=< your static domain > 5000``` 

# Future
- [ ] Improve performance of the Slack service. 
- [ ] Improve the handling of messages containing HTML. 
- [ ] Fix issue with filters being unavailable after scrolling through messages.
- [ ] Fix issue with the opening of Outlook messages when the user does not have a cookie. 
- [ ] Extend the new messages feature by updating the color of the Notigather favicon and producing an audible alert when a new notification is detected. 
- [ ] Add button to account recovery page that allows the user to return to the login page. 
- [ ] Add feature to indicate that services have been authenticated and allow for users to disable services. 
- [ ] Add feature for collapsing all messages.
- [ ] Include additional messaging services such as Microsoft Teams, Jira, Bitbucket, and others.  
- [ ] Publicly hosted through the Google Cloud Platform. This change would include transitioning to a cloud RDBMS and orchestrating the application with Kubernetes. 
 





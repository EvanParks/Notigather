from Mailer_interface import IMailer
import smtplib
from email.message import EmailMessage 

class Mailer(IMailer):     
    def print_mailer(self):
        print("Mailer") 

    #Information for sending an email was pulled from https://stackoverflow.com/questions/77340573/python-script-for-sending-an-email-via-gmail-refuses-to-accept-username-and-app 
    def send_email(self, **kwargs):
        email = kwargs.get('email')
        token = kwargs.get('token')
        user_id = kwargs.get('user_id')
        database = kwargs.get('database')

        result = self.store_token(token, user_id, database)

        if result:
            msg = EmailMessage() 

            msg['Subject'] = "Password Reset Link"
            msg['From'] = "NotiGather@gmail.com"
            msg['To'] = [email]
            msg.set_content(f"http://localhost:3000/RecoverAccount?token={token}")

            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login('NotiGather@gmail.com', 'azbt rrao edlz einh') 
                server.send_message(msg)
            except Exception as e:
                print(f"An error occurred: {e}")
            finally:
                server.quit()
            print('Message sent')
        else:
            print('Message not sent')

    def store_token(self, token, user_id, database): 
        if self.check_user_id(user_id, database):
            query = "UPDATE user_credentials SET token = ? where id = ?"
            parameters = (token, user_id) 

            database.execute_query(query=query, parameters=parameters)
            database.close_database()

            return True 
        else:
            return False 

    def check_user_id(self, user_id, database):
        user_id = int(user_id) 

        query = "SELECT COUNT(*) FROM user_credentials where id = ?"
        parameters = (user_id,)

        result = database.execute_query(query=query, parameters=parameters)
        return result[0][0] > 0


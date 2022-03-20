from twilio.rest import Client
import json, os

with open('/etc/config.json') as config_file:
    config = json.load(config_file)

# Your Account Sid and Auth Token from twilio.com/console
# and set the environment variables. See http://twil.io/secure
account_sid = config.get('TWILIO_ACCOUNT_SID')
auth_token = config.get('TWILIO_AUTH_TOKEN')
client = Client(account_sid, auth_token)

def phone_msg_verify(verify_code, phone_number_to):
    message = client.messages.create(
            body=f'Your verification code is : {verify_code}, you are even closer to starting your money making process!',
            from_='+14432965265',
            to=f'{phone_number_to}'
        )

def new_user(name):
    message = client.messages.create(
        body=f'NEW ACCOUNT {name}',
        from_='+14432965265',
        to=['+16473948541', '+4915784096334']
    )

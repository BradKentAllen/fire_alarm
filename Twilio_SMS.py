# Twilio_SMS.py

''' Twilio SMS text send utility
API key stored in giblets.py
Message must be a string
'''

# Rev 1.0  created Feb 8, 2022 using NEXMO as template

from twilio.rest import Client

# Twilio auth is in giblets
from giblets import twilio_phone_number, twilio_API_sid, twilio_API_token

def send_SMS_message(message, phone_number, *args):
    '''sends SMS text using nexmo'''
    client = Client(twilio_API_sid, twilio_API_token)

    phoneList = [phone_number]
    if args:
        for phone in args:
            phoneList.append(phone)

    if type(message) is str:
        
        print('send message to:', end=' ')

        for phone in phoneList:
            print(phone, end=', ')
            message = client.messages.create(
                to=phone_number, 
                from_=twilio_phone_number,
                body=message)

    else:
        raise ValueError('Twilio message must be a string')

    print('')


if __name__ == '__main__':
    print('start Twilio test')
    message = 'test message This One'
    phone_number = "+14259856203"
    send_SMS_message(message, phone_number)
    #print(f'{message} sent to {phone_number}')




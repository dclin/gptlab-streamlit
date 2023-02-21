import hashlib
import binascii
import uuid 
import datetime 
import pytz 


# general helper function 
def generate_uuid():
    return str(uuid.uuid4())

def hash_user_string(user_string):
    salt = user_string.encode()
    iterations = 200000
    key = hashlib.pbkdf2_hmac('sha256', user_string.encode(), salt, iterations)
    return binascii.hexlify(key).decode()

def get_current_time():
    return datetime.datetime.now(pytz.timezone('US/Pacific'))

def clean_display_message_str(message, restart_sequence, stop_sequence):
    return message.replace(restart_sequence,"").replace(stop_sequence,"").replace("\n","  \n").replace("\\n","  \n")

def clean_message_str(message, restart_sequence, stop_sequence):
    return message.replace(restart_sequence,"").replace(stop_sequence,"").replace("\n","\\n")

def clean_prompt_message_str(message):
    return message.replace("\n","\\n")


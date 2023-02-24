import hashlib
import binascii
import uuid 
import datetime 
import pytz 
from cryptography.fernet import Fernet
import base64


# general helper function 
def generate_uuid():
    return str(uuid.uuid4())

def hash_user_string(user_string):
    salt = user_string.encode()
    iterations = 200000
    key = hashlib.pbkdf2_hmac('sha256', user_string.encode(), salt, iterations)
    return binascii.hexlify(key).decode()

## private function to convert hex-encoded user hash value, converts to byte, and encode as URL-safe base64 string
def _generate_user_key(user_hash):
    return base64.urlsafe_b64encode(bytes.fromhex(user_hash))

# encrypt user message using Fernet encryption  
# Fernet uses AES-128 in CBC mode with PKCS7 padding 
# user hash is used to generate the symmetric key 
def encrypt_user_message(user_hash, user_message):
    user_message_byte = user_message.encode('utf-8')
    cipher = Fernet(_generate_user_key(user_hash))
    return cipher.encrypt(user_message_byte)

# decrypt user message using Fernet encryption 
# user hash is used to generate the symmetric key 
def decrypt_user_message(user_hash, cipher_text):
    cipher = Fernet(_generate_user_key(user_hash))
    return cipher.decrypt(cipher_text).decode('utf-8')


def get_current_time():
    return datetime.datetime.now(pytz.timezone('US/Pacific'))

def clean_display_message_str(message, restart_sequence, stop_sequence):
    return message.replace(restart_sequence,"").replace(stop_sequence,"").replace("\n","  \n").replace("\\n","  \n")

def clean_message_str(message, restart_sequence, stop_sequence):
    return message.replace(restart_sequence,"").replace(stop_sequence,"").replace("\n","\\n")

def clean_prompt_message_str(message):
    return message.replace("\n","\\n")


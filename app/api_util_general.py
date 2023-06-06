import hashlib
import binascii
import uuid 
import datetime 
import pytz 
from cryptography.fernet import Fernet
import base64
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging 
import streamlit as st 


# basic logging configuration 
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

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
    cipher = Fernet(_generate_user_key(user_hash + st.secrets["util"]["global_salt"]))
    return cipher.encrypt(user_message_byte)

# decrypt user message using Fernet encryption 
# user hash is used to generate the symmetric key 
def decrypt_user_message(user_hash, cipher_text):
    cipher = Fernet(_generate_user_key(user_hash + st.secrets["util"]["global_salt"]))
    return cipher.decrypt(cipher_text).decode('utf-8')


def get_current_time():
    return datetime.datetime.now(pytz.timezone('US/Pacific'))


def format_datetime(dt):
    # Format the datetime object
    formatted_dt = dt.strftime('%Y-%m-%d %H:%M %Z')
    return formatted_dt


def clean_display_message_str(message, restart_sequence, stop_sequence):
    return message.replace(restart_sequence,"").replace(stop_sequence,"").replace("\n","  \n").replace("\\n","  \n")

def clean_message_str(message, restart_sequence, stop_sequence):
    return message.replace(restart_sequence,"").replace(stop_sequence,"").replace("\n","\\n")

def clean_prompt_message_str(message):
    return message.replace("\n","\\n")


def get_cosine_similarity(str1, str2):
    """
    Compute the cosine similarity between two input strings, represented as feature vectors.

    The strings are first vectorized using the TfidfVectorizer class from scikit-learn,
    which converts the text into a sparse matrix of tf-idf features, where each row corresponds to a document
    (in this case, a single string), and each column corresponds to a unique term from the input corpus.
    The tf-idf values for each term in each document are computed using the following formula:

    tf-idf(i, j) = tf(i, j) * log(N / df(j))

    where i is the index of the document, j is the index of the term, tf(i, j) is the term frequency in the document,
    N is the total number of documents, and df(j) is the number of documents that contain the term.

    The resulting feature vectors are then compared using the cosine similarity metric,
    which measures the cosine of the angle between the vectors. A value of 1 indicates identical vectors,
    while a value of 0 indicates completely dissimilar vectors.

    Args:
        str1 (str): The first input string to compare.
        str2 (str): The second input string to compare.

    Returns:
        float: The cosine similarity between the two input strings, in the range [0, 1].
    """

    # Create a TfidfVectorizer object
    corpus = [str1, str2]
    vect = TfidfVectorizer(min_df=1,stop_words='english')

    tfidf = vect.fit_transform(corpus)
    # Compute the cosine similarity between the two vectors
    cos_sim = cosine_similarity(tfidf[0], tfidf[1])[0][0]

    return cos_sim 

def datetime_serializer(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    else:
        return str(obj)
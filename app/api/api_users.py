from api import api_util_firebase as fu 
from api import api_util_general as gu 
from api import api_util_openai as ou

class users:

    class UserNotFound(Exception):
        pass

    class BadRequest(Exception):
        pass

    class OpenAIClientCredentialError(Exception):
        pass

    class DBError(Exception):
        pass

    def __init__(self):
        self.db = fu.firestore_db()

    def find_user(self, user_string):
        user_hash = gu.hash_user_string(user_string)
        user = self.db.get_doc(collection_name="users", document_id=user_hash)
        if user:     
            return user
        else:
            raise self.UserNotFound("User not found")

    def get_user(self, user_id):
        user = self.db.get_doc(collection_name="users", document_id=user_id)
        if user:
            return user
        else:
            raise self.UserNotFound("User not found")

    def get_users(self):
        users = self.db.get_docs(collection_name="users")
        if len(users) > 0 :
            return users

    def update_user_stats(self, user_id, metric_value_pairs):
        user = self.get_user(user_id)
        
        if not user:
            raise self.UserNotFound("User not found")

        if metric_value_pairs == None:
            raise self.BadRequest("Bad request: need to supply (metric, value) pairs")

        for metric_value_pair in metric_value_pairs:
            try:
                float(str(metric_value_pair[1]))
            except:
                raise self.BadRequest("Bad request: need numeric values ")

        for metric_value_pair in metric_value_pairs:
            self.db.increment_document_fields(collection_name="users", document_id=user_id, field_name=metric_value_pair[0], increment=metric_value_pair[1])

    def create_user(self, api_key):
        try:
            user = self.find_user(user_string=api_key)
            raise self.BadRequest("Bad request: user exists")
        except self.UserNotFound:
            pass

        o = ou.open_ai(api_key=api_key, restart_sequence='|USER|', stop_sequence='|SP|')
        key_validated = o.validate_key()
        if key_validated == False:
            raise self.BadRequest("Bad request: OPENAI API Key Invalid")

        user_hash = gu.hash_user_string(api_key)

        user_dict = {
            'user_hash': user_hash,
            'user_hash_type': 'open_ai_key',
            'created_date': gu.get_current_time(),
            'last_modified_date': gu.get_current_time()
        }

        user_id = self.db.create_doc(collection_name="users",data=user_dict, id=user_hash)
        return user_id 


    def get_create_user(self, api_key):
        o = ou.open_ai(api_key=api_key, restart_sequence='|USER|', stop_sequence='|SP|')
        key_validated = o.validate_key()
        if key_validated == False:
            raise self.OpenAIClientCredentialError("Bad request: OPENAI API Key Invalid")

        try:
            user = self.find_user(user_string=api_key)
            return user
        except self.UserNotFound:
            pass

        user_hash = gu.hash_user_string(api_key)

        user_dict = {
            'user_hash': user_hash,
            'user_hash_type': 'open_ai_key',
            'created_date': gu.get_current_time(),
            'last_modified_date': gu.get_current_time()
        }

        user_id = self.db.create_doc(collection_name="users",data=user_dict, id=user_hash)

        if not user_id:
            raise self.DBRecordError("DB Record Error: user not created")       

        user = self.get_user(user_id=user_id)

        return user 


## TEST 
# u = users()

# try:
#     user_id = u.create_user(api_key='adfasdfsd')
#     print(user_id)
# except Exception as e:
#     error_message = str(e)
#     error_code = type(e).__name__
#     print("Error message:", error_message)
#     print("Error code:", error_code)


# metric_value_pairs = [('sessions_started',5)]

# try:
#     u.update_user_stats('xxxxxx',metric_value_pairs)
# except Exception as e:
#     error_code = type(e).__name__
#     print("Error code:", error_code )


#print(u.get_users())

# try:
#     user_id = u.find_user('adfadsfd')
#     print(user_id)
# except Exception as e:
#     error_message = str(e)
#     error_code = type(e).__name__
#     print("Error message:", error_message)
#     print("Error code:", error_code)


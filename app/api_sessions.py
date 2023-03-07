import api_util_firebase as fu 
import api_util_general as gu 
import api_util_openai as ou
import api_bots as bu 
import api_users as uu
import enum 
import json 

class sessions:

    class BadRequest(Exception):
        pass

    class SessionNotRecorded(Exception):
        pass

    class MessageNotRecorded(Exception):
        pass
    
    class PromptNotRecorded(Exception):
        pass 

    class SessionAttributeNotUpdated(Exception):
        pass 

    class DBRecordError(Exception):
        pass

    class DBAttributeError(Exception):
        pass
    
    class OpenAIClientConnectionError(Exception):
        pass
    
    class OpenAIConnectionError(Exception):
        pass

    class OpenAIClientCredentialError(Exception):
        pass 

    class OpenAIClientRateLimitError(Exception):
        pass


    class SessionStatus(enum.Enum):
        STARTED = 0
        COMPLETED = 1
        USER_ABANDONED = 2
        SYSTEM_ABANDONED = 3

    class UserLiked(enum.Enum):
        DISLIKED = 0
        LIKED = 1


    def __init__(self, user_hash):
        self.db = fu.firestore_db()
        self.openai_stop_sequence = '|SP|'
        self.openai_restart_sequence = '|USER|'
        self.user_hash = user_hash

    def create_session(self, user_id, oai_api_key, bot_id=None, bot_config_dict=None):
        """
        Creates a new chat session for a user_id, using a specific OpenAI API Key. 
        The session can associated with a specific bot id or just a bot config (during the lab).
        Session messages are only recorded as sub-collection items for a session with a specific bot.
        """

        try: 
            if bot_id != None:
                new_session = self._create_session(user_id=user_id, bot_id=bot_id)
            if bot_config_dict != None: 
                new_session = self._create_session(user_id=user_id, bot_config_dict=bot_config_dict)
            if bot_id == None and bot_config_dict == None: 
                raise self.BadRequest("Bad request: missing both Assistant ID and Assistant config")
        except Exception as e: 
            raise 

        try: 
            bot_response = self.get_session_response(session_id=new_session['session_id'], oai_api_key=oai_api_key)
        except Exception as e: 
            raise 

        if bot_id != None:
            # increment user's and bot's sessions_started field
            try:
                user_field_incremented = self.db.increment_document_fields(collection_name="users", document_id=user_id, field_name='sessions_started', increment=1)
                bot_field_incremented = self.db.increment_document_fields(collection_name="bots", document_id=bot_id, field_name='sessions_started', increment=1)
            except:
                pass # swallow exceptions on purpose 

        return {
            'session_info': new_session, 
            'session_response': bot_response 
        }


    def get_session_response(self, session_id, oai_api_key, user_message=None):
        """
        Main method to get a bot chat response

        Latest messages list string is always stored in the session doc. Allowing conversations to be restarted with the bot.

        If the session is associatd with a specific bot_id, it would record every single messages as a sub-collection item as well.
        """
        current_session =  self.db.get_doc(collection_name="sessions", document_id=session_id)
        if current_session == None:
            raise self.BadRequest("Bad request: session not found")
                      
        o = ou.open_ai(api_key=oai_api_key, restart_sequence=self.openai_restart_sequence, stop_sequence=self.openai_stop_sequence)

        current_session_messages = []
        content_moderation_check = {'flagged':0,'flagged_categories':[]}

        record_message = False 

        if current_session['data']['bot_id']:
            record_message = True 

        if current_session['data']['messages_str'] != None:
            current_session_messages = json.loads(gu.decrypt_user_message(user_hash=self.user_hash, cipher_text=current_session['data']['messages_str']))

            # this means the conversation last ended with bot message, so just return that
            if current_session_messages[-1]['role'] == 'assistant' and user_message == None:
                return  { 
                    'bot_message': current_session_messages[-1]['message'],
                    'prompt_injection_detected': 0,
                    'messages_condensed': 0,
                    'user_message_flagged': 0,
                    'user_message_flagged_categories': []
                }

        if user_message != None: 
            user_message = user_message.replace("\"","'")
            try:
                self._record_session_message(session_id=session_id, message=user_message, is_user=True, record_message=record_message)
            except Exception as e: 
               raise

            try: 
                content_moderation_check = o.get_moderation(user_message=user_message)
                current_session_messages.append({'role':'user','message':user_message,'created_date':gu.get_current_time()})
            except o.ClientConnectionError as e:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.OpenAIClientConnectionError("Cannot establish connection with OpenAI. Check your connection.")
            except o.VendorConnectionError as e:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.OpenAIConnectionError("OpenAI is experiencing difficulities now. Try again later.")
            except o.ClientCredentialError as e:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.OpenAIClientCredentialError("OpenAI credential error. API key may be invalid, expired, revoked, or does not have right permissions.")
            except o.ClientRateLimitError as e:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.OpenAIClientRateLimitError("OpenAI Rate Limit exceeded. Try again later.")
            except o.ClientRequestError as e:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.BadRequest("Bad Request: Bad OpenAI Request")

        try:
            responded_messages = o.get_ai_response(
                model_config_dict=current_session['data']['bot_model_config'],
                init_prompt_msg=current_session['data']['bot_initial_prompt_msg'], 
                messages=current_session_messages,
                summary_prompt_msg=current_session['data']['bot_summary_prompt_msg'],
                session_type=current_session['data']['bot_session_type']
            )
        except o.ClientConnectionError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.OpenAIClientConnectionError("Cannot establish connection with OpenAI. Check your connection.")
        except o.VendorConnectionError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.OpenAIConnectionError("OpenAI is experiencing difficulities now. Try again later.")
        except o.ClientCredentialError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.OpenAIClientCredentialError("OpenAI credential error. API key may be invalid, expired, revoked, or does not have right permissions.")
        except o.ClientRateLimitError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.OpenAIClientRateLimitError("OpenAI Rate Limit exceeded. Try again later.")
        except o.ClientRequestError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.BadRequest("Bad Request: Bad OpenAI Request")

        try:
            self._update_session_messages(session_id, responded_messages)
            self._record_session_message(session_id=session_id, message=responded_messages['messages'][-1]['message'], is_user=False, record_message=record_message)
        except Exception as e: 
            raise 

        return {
            'bot_message': responded_messages['messages'][-1]['message'],
            'prompt_injection_detected': responded_messages['prompt_injection_detected'],
            'messages_condensed': responded_messages['messages_condensed'],
            'user_message_flagged': content_moderation_check['flagged'],
            'user_message_flagged_categories': content_moderation_check['flagged_categories']
        }


    # main function to end a session 
    def end_session(self, session_id, end_status=SessionStatus.COMPLETED.value):

        current_session =  self.db.get_doc(collection_name="sessions", document_id=session_id)
        if current_session == None:
            raise self.BadRequest("Bad request: session not found")

        if end_status not in [e.value for e in self.SessionStatus]:
            raise self.BadRequest("Invalid end_status value")

        status_update = {'status': end_status}
        record_status = self.db.update_document_fields(collection_name="sessions", document_id=session_id, updates=status_update)

        if record_status == None:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.SessionAttributeNotUpdated("Session status not changed accordingly")

        if end_status == self.SessionStatus.COMPLETED.value:
            # increment user's and bot's sessions_started field
            try:
                user_field_incremented = self.db.increment_document_fields(collection_name="users", document_id=current_session['data']['user_id'], field_name='sessions_ended', increment=1)
                bot_field_incremented = self.db.increment_document_fields(collection_name="bots", document_id=current_session['data']['bot_id'], field_name='sessions_ended', increment=1)
            except:
                pass # swallow exceptions on purpose 
        return True


    # rate a session 
    def rate_session(self, session_id, user_liked=UserLiked.LIKED.value):
        # make sure session is legit 
        current_session =  self.db.get_doc(collection_name="sessions", document_id=session_id)
        if current_session == None:
            raise self.BadRequest("Bad request: session not found")

        # make sure user_liked is a valid enum value 
        if user_liked not in [u.value for u in self.UserLiked]:
            raise self.BadRequest("Invalid end_status value")

        user_liked_update = {'user_liked': user_liked}
        record_user_liked = self.db.update_document_fields(collection_name="sessions", document_id=session_id, updates=user_liked_update)

        if record_user_liked == None:
            pass # swallow the exception (since NBD)

    # internal function to just create a session 
    def _create_session(self, user_id, bot_id=None, bot_config_dict=None):
        bot = bu.bots()

        if bot_id != None:
            # for now, skipping making sure user exists 
            try:
                bot_dict = bot.get_bot(bot_id)
            except bot.BotNotFound as e:
                raise self.BadRequest("Bad Request: Assistant not found")
            except bot.BotIncomplete as e:
                raise self.BadRequest("Bad Request: Assistant is not fully configured")
            except Exception as e:
                raise self.BadRequest("Bad Request: Unknown error")
           
        
        if bot_config_dict != None: 
            bot_config_validated = self._validate_bot_config(bot_config_dict=bot_config_dict)
            if bot_config_validated == False: 
                raise self.BadRequest("Bad Request: Assistant Config Missing Required Fields")
            bot_dict = bot_config_dict 

        try:
            session_type = bot.get_session_type(bot_dict['session_type'])
        except Exception as e: 
            raise        

        # session dictionary 
        # updating data model - caching prompt messages and model configs - to avoid having to read bot dict for values 
        session_dict = {
            'user_id': user_id, 
            'bot_id': bot_id,
            'bot_session_type': session_type,
            'bot_initial_prompt_msg': bot_dict['initial_prompt_msg'],
            'bot_summary_prompt_msg': bot_dict['summary_prompt_msg'],
            'bot_model_config': bot_dict['model_config'],
            'status': self.SessionStatus.STARTED.value,
            'created_date': gu.get_current_time(),
            'message_count': 0,
            'messages_str': None,
            'session_schema_version': 1
        }
        # create the session 
        session_id = self.db.create_doc(collection_name="sessions", data=session_dict)

        if not session_id:
            raise self.DBRecordError("DB Record Error: session not created")
        
        return {'session_id': session_id, 'session_data': session_dict}

    # internal function to remember the message dictionaries:
    def _update_session_messages(self, session_id, message_response_dict):
        # get session 
        current_session =  self.db.get_doc(collection_name="sessions", document_id=session_id)
        if current_session == None:
            raise self.BadRequest("Bad request: session not found")
        
        message_str = json.dumps(message_response_dict['messages'], default=gu.datetime_serializer)
        encrypted_msg_str = gu.encrypt_user_message(user_hash=self.user_hash, user_message=message_str)
        session_msg_update_dict = {'messages_str': encrypted_msg_str}

        record_new_msg = self.db.update_document_fields(collection_name="sessions", document_id=session_id, updates=session_msg_update_dict)

        if record_new_msg == None:
            raise self.DBAttributeError("DB Attribute Error: session messages not updated")

        return True 
    
    # internal function to recod each session message:
    def _record_session_message(self, session_id, message, is_user, record_message=True):
        if record_message:
            msg_role = 'user'

            if is_user == False:
                msg_role = 'assistant'

            msg_dict = {
                'message':gu.encrypt_user_message(user_hash=self.user_hash, user_message=message.replace(self.openai_restart_sequence,"").replace(self.openai_stop_sequence,"")),#.replace("\n","\\n"),
                'role':msg_role,
                'created_date':gu.get_current_time()
            }
            message_id = self.db.create_sub_collection_item(collection_name="sessions", document_id=session_id, sub_collection_name="messages", data=msg_dict)
            if message_id == None:
                raise self.DBRecordError("DB Record Error: message not recorded")

        # increment message count fields
        message_incremented = self.db.increment_document_fields(collection_name="sessions", document_id=session_id, field_name='message_count', increment=1)
        if message_incremented == None:
            pass # swallow exception for now 
            #raise self.DBAttributeError("DB Attribute Error: message_count not recorded")

        return True    

    def _validate_bot_config(self, bot_config_dict):
        required_fields = ['session_type', 'initial_prompt_msg', 'summary_prompt_msg', 'model_config']
        model_config_fields = ['model', 'temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']
        
        for field in required_fields:
            if field not in bot_config_dict:
                return False
            
        model_config = bot_config_dict['model_config']
        for field in model_config_fields:
            if field not in model_config:
                return False
            
        return True


#### TESTING #### 
# user_id = ''
# user_hash = ''
# bot_id = ''

# # bot_config = {
# #     'session_type': 'COACHING',
# #     'initial_prompt_msg': ' ',
# #     'summary_prompt_msg': ' ',
# #     'model_config': {
# #         'frequency_penalty': 0.5, 
# #         'temperature': 1.0, 
# #         'model': 'text-davinci-003', 
# #         'presence_penalty': 1.0, 
# #         'max_tokens': 250, 
# #         'top_p': 1.0
# #     }
# # }

# # #session_id = ''
# api_key = ''

# s = sessions(user_hash=user_hash)

# # my_session = s.create_session(user_id=user_id, bot_config_dict=bot_config, oai_api_key=api_key)
# my_session = s.create_session(user_id=user_id, bot_id=bot_id, oai_api_key=api_key)
# print(my_session)
# print("\n")

# session_id = my_session['session_info']['session_id']

# print("\n")
# user_input = ''

# while user_input != 'quit':
#     user_input=input("Type your message to Brian:")
#     print("\n")
#     print(s.get_session_response(session_id=session_id, oai_api_key=api_key, user_message=user_input))

import api_util_firebase as fu 
import api_util_general as gu 
import api_util_openai as ou
import api_bots as bu 
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

    class OpenAIError(Exception):
        def __init__(self, message, error_type=None):
            super().__init__(message)
            self.error_type = error_type 

    class SessionStatus(enum.Enum):
        STARTED = 0
        COMPLETED = 1
        USER_ABANDONED = 2
        SYSTEM_ABANDONED = 3
        SYSTEM_ABANDONED_OPENAI = 4

    class UserLiked(enum.Enum):
        DISLIKED = 0
        LIKED = 1


    def __init__(self, user_hash):
        self.db = fu.firestore_db()
        self.openai_stop_sequence = '|SP|'
        self.openai_restart_sequence = '|USER|'
        self.user_hash = user_hash

    def create_session(self, user_id, oai_api_key, bot_id=None, bot_config_dict=None, overwritten_model=None):
        """
        Creates a new chat session for a user_id, using a specific OpenAI API Key. 
        The session can associated with a specific bot id or just a bot config (during the lab).
        Session messages are only recorded as sub-collection items for a session with a specific bot.
        """

        try: 
            if bot_id != None:
                new_session = self._create_session(user_id=user_id, bot_id=bot_id, overwritten_model=overwritten_model)
            elif bot_config_dict != None: 
                new_session = self._create_session(user_id=user_id, bot_config_dict=bot_config_dict)
            else: 
                raise self.BadRequest("Bad request: missing both Assistant ID and Assistant config")
        except Exception as e: 
            raise 
        
        try: 
            bot_response = self.get_session_response(session_id=new_session['session_id'], oai_api_key=oai_api_key)
        except self.OpenAIError as e: 
            gu.logging.warning(f"Newly created session {new_session['session_id']} status SYSTEM_ABANDONED_OPENAI | OpenAIError | Exception: {e}")
            self.end_session(session_id=new_session['session_id'], end_status=self.SessionStatus.SYSTEM_ABANDONED_OPENAI.value)
            raise self.OpenAIError(f"{str(e)}", error_type=e.error_type) from e 

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
            except o.OpenAIError as e: 
                if e.error_type == "RateLimitError":
                    gu.logging.warning(f"Session {session_id} moderation check impacted due to OpenAI rate limit | OpenAIError | Exception: {e}") 
                else:
                    gu.logging.warning(f"Session {session_id} status SYSTEM_ABANDONED_OPENAI | OpenAIError | Exception: {e}")
                    self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED_OPENAI.value)
                raise self.OpenAIError(f"{str(e)}", error_type=e.error_type) from e 

        try:
            responded_messages = o.get_ai_response(
                model_config_dict=current_session['data']['bot_model_config'],
                init_prompt_msg=current_session['data']['bot_initial_prompt_msg'], 
                messages=current_session_messages,
                summary_prompt_msg=current_session['data']['bot_summary_prompt_msg'],
                session_type=current_session['data']['bot_session_type']
            )
        except o.OpenAIError as e: 
            if e.error_type == "RateLimitError":
                gu.logging.warning(f"Session {session_id} response impacted due to OpenAI rate limit | OpenAIError | Exception: {e}") 
            else:
                gu.logging.warning(f"Session {session_id} status SYSTEM_ABANDONED_OPENAI | OpenAIError | Exception: {e}")
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED_OPENAI.value)
            raise self.OpenAIError(f"{str(e)}", error_type=e.error_type) from e 
        except Exception as e: 
            raise 

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
            gu.logging.warning(f"Session {session_id} status SYSTEM_ABANDONED | SessionAttributeNotUpdated | Exception: Session status {end_status} not set accordingly")
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


    # get a user's past sessions with a bot 
    def get_past_sessions(self, user_id, bot_id):

        query_filters = [("user_id","==",user_id),("bot_id","==",bot_id),("session_schema_version","==",1)]
        session_docs = self.db.get_docs(collection_name="sessions", query_filters=query_filters, order_by_field="created_date", order_by_direction="DESCENDING", limit=50)

        sessions = []

        if session_docs:

            for s in session_docs:
                sessions.append({
                    'id': s['id'],
                    'created_date': s['data']['created_date'],
                    'message_count': s['data']['message_count'],
                    'status': s['data']['status'],
                    'bot_model': s['data']['bot_model_config']['model']
                })
        
        return sessions 

    # get a user's messages from a session 
    def get_session_messages(self, session_id):

        message_docs = self.db.get_sub_collection_items(
            collection_name="sessions", 
            document_id=session_id, 
            sub_collection_name="messages", 
            order_by_field="created_date", 
            order_by_direction="ASCENDING")

        messages = []

        for m in message_docs: 
            messages.append({
                'role':m['data']['role'],
                'created_date':m['data']['created_date'],
                'message':gu.decrypt_user_message(user_hash=self.user_hash, cipher_text=m['data']['message'])
            })

        return messages 


    # internal function to just create a session 
    def _create_session(self, user_id, bot_id=None, bot_config_dict=None, overwritten_model=None):
        bot = bu.bots()

        if bot_id != None:
            # for now, skipping making sure user exists 
            try:
                bot_dict = bot.get_bot(bot_id)
                if overwritten_model != None: 
                    bot_dict['model_config']['model'] = overwritten_model
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
        except ValueError as e: 
            raise self.BadRequest("Bad Request: Assisant configured with unknown session type")       

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

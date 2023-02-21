import api_util_firebase as fu 
import api_util_general as gu 
import api_util_openai as ou
import api_bots as bu 
import api_users as uu
import enum 
# Testing only 
# import streamlit as st 

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


    def __init__(self):
        self.db = fu.firestore_db()
        self.openai_stop_sequence = '|SP|'
        self.openai_restart_sequence = '|USER|'

    # main function to create a session 
    def create_session(self, user_id, bot_id, ai_key): 

        # validate OpenAI Key 
        # o = ou.open_ai(api_key=ai_key, restart_sequence=self.openai_restart_sequence, stop_sequence=self.openai_stop_sequence)
        # key_validated = o.validate_key()
        # if key_validated == False:
        #     raise self.OpenAIClientCredentialError("Bad request: OPENAI API Key Invalid")

        try:    
            session_info_dict = self._create_session(user_id=user_id, bot_id=bot_id)
        except self.BadRequest as e:
            raise self.BadRequest("Bad request: user or bot not found")
        except self.DBRecordError as e:
            raise self.SessionNotRecorded("DB Error: session not created")

        try:
            session_response = self.get_session_response(\
                session_id = session_info_dict['session_id'], \
                ai_key = ai_key
            )
        except self.BadRequest as e:
            raise self.BadRequest("Something went wrong.")

        except self.OpenAIConnectionError as e:
            raise self.OpenAIConnectionError("OpenAI is experiencing some difficulties")

        except self.OpenAIClientCredentialError as e:
            raise self.OpenAIClientCredentialError("OpenAI credential invalid or revoked.")

        except self.OpenAIClientRateLimitError as e:
            raise self.OpenAIClientRateLimitError("OpenAI Rate Limit Reached")

        except self.OpenAIClientConnectionError as e:
            raise self.OpenAIClientConnectionError("Connection error. Could not connect to OpenAI")

        except self.PromptNotRecorded as e:
            raise self.PromptNotRecorded("Something went wrong.")

        except self.MessageNotRecorded as e:
            raise self.MessageNotRecorded("Something went wrong.")

        except self.SessionAttributeNotUpdated as e:
            raise self.SessionAttributeNotUpdated("Something went wrong.")

        # increment user's and bot's sessions_started field
        try:
            user_field_incremented = self.db.increment_document_fields(collection_name="users", document_id=user_id, field_name='sessions_started', increment=1)
            bot_field_incremented = self.db.increment_document_fields(collection_name="bots", document_id=bot_id, field_name='sessions_started', increment=1)
        except:
            pass # swallow exceptions on purpose 

        return session_response
        


    # main function to get a bot response 
    def get_session_response(self, session_id, ai_key, user_message=None):

        # get session 
        current_session =  self.db.get_doc(collection_name="sessions", document_id=session_id)
        if current_session == None:
            raise self.BadRequest("Bad request: session not found")

        bot = bu.bots()
        try:
            bot_dict = bot.get_bot(bot_id=current_session['data']['bot_id'], model_id=current_session['data']['bot_model_config_id'], prompt_id=current_session['data']['bot_prompt_id'])
        except bot.BotNotFound as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.BadRequest("Bad Request: Bot not found")
        except bot.BotIncomplete as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.BadRequest("Bad Request: Bot is not fully configured")
        except Exception as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.BadRequest("Bad Request: Unknown error")

        # validate OpenAI Key 
        o = ou.open_ai(api_key=ai_key, restart_sequence=self.openai_restart_sequence, stop_sequence=self.openai_stop_sequence)
        # key_validated = o.validate_key()
        # if key_validated == False:
        #     self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
        #     raise self.OpenAIClientCredentialError("Bad request: OPENAI API Key Invalid")
        
        next_prompt = '' 

        if user_message:
            # get last prompt from session 

            last_prompt = self.db.get_sub_collection_item(collection_name="sessions", document_id=session_id, sub_collection_name="prompts", sub_document_id=current_session['data']['current_prompt_id'])
            if last_prompt == None:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.SessionAttributeNotUpdated("Bad request: session did not have last prompt recorded")

            next_prompt = next_prompt + last_prompt['data']['message'] + user_message + self.openai_stop_sequence 

            # record the next prompt  
            try:
                prompt_recorded = self._record_session_prompt(session_id = session_id, prompt_message = next_prompt)
            except self.DBRecordError as e:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.PromptNotRecorded("DB Record Error: next prompt could not be recorded")
            except self.DBAttributeError as e:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.SessionAttributeNotUpdated("Next prompt ID could not be recorded on session")

            # record user message 
            try:
                message_recorded = self._record_session_message( \
                    session_id=session_id, \
                    message=gu.clean_message_str(message=user_message, restart_sequence=self.openai_restart_sequence, stop_sequence=self.openai_stop_sequence), \
                    is_user=True)
            except self.DBRecordError as e:
                self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
                raise self.MessageNotRecorded("DB Record Error: message could not be recorded")
            except self.DBAttributeError as e:
                pass # swalllow attribute errors 

        # get bot message from openai 
        try:
            submitted_msg = bot_dict['initial_prompt_msg'] + self.openai_stop_sequence + next_prompt
            msg_completion = o.get_completion(model_config_dict=bot_dict['model_config'], message=submitted_msg)
        except o.ClientConnectionError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.OpenAIClientConnectionError("Cannot establish connection with OpenAI. Check your connection.")
        except o.VendorConnectionError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.OpenAIConnectionError("OpenAI is experiencing difficulities now. Try again later.")
        except o.ClientCredentialError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.OpenAIClientCredentialError("OpenAI key invalid.")
        except o.ClientRateLimitError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.OpenAIClientRateLimitError("OpenAI Rate Limit exceeded. Try again later.")
        except o.ClientRequestError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.BadRequest("Bad Request: Bad OpenAI Request")

        bot_message = msg_completion['choices'][0]['text']
        total_token_count = msg_completion['usage']['total_tokens']

        # prepare next prompt 
        next_prompt = next_prompt + bot_message + self.openai_restart_sequence 

        # record the next prompt  
        try:
            prompt_recorded = self._record_session_prompt(session_id = session_id, prompt_message = next_prompt)
        except self.DBRecordError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.PromptNotRecorded("DB Record Error: next prompt could not be recorded")
        except self.DBAttributeError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.SessionAttributeNotUpdated("Next prompt ID could not be recorded on session")

        # record user message 
        try:
            message_recorded = self._record_session_message( \
                session_id=session_id, \
                message=gu.clean_message_str(message=bot_message, restart_sequence=self.openai_restart_sequence, stop_sequence=self.openai_stop_sequence), \
                is_user=False, \
                total_token=msg_completion['usage']['total_tokens'])

            return {'session_id':session_id, 'response_message':bot_message, 'total_tokens':msg_completion['usage']['total_tokens']}

        except self.DBRecordError as e:
            self.end_session(session_id=session_id, end_status=self.SessionStatus.SYSTEM_ABANDONED.value)
            raise self.MessageNotRecorded("DB Record Error: message could not be recorded")
        except self.DBAttributeError as e:
            pass # swalllow attribute errors 


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
            pass # swallow 


        return True 

    # internal function to just create a session 
    def _create_session(self, user_id, bot_id):

        # # make sure user exists 
        # user = uu.users()
        # try:
        #     user_dict = user.get_user(user_id)
        # except user.UserNotFound as e:
        #     raise self.BadRequest("Bad Request: User not found")
        # except Exception as e:
        #     raise self.BadRequest("Bad Request: Unknown error")

        # make sure bot exists                 
        bot = bu.bots()
        try:
            bot_dict = bot.get_bot(bot_id)
        except bot.BotNotFound as e:
            raise self.BadRequest("Bad Request: Bot not found")
        except bot.BotIncomplete as e:
            raise self.BadRequest("Bad Request: Bot is not fully configured")
        except Exception as e:
            raise self.BadRequest("Bad Request: Unknown error")

        # session dictionary 
        session_dict = {
            'user_id':user_id,
            'bot_id':bot_dict['id'],
            'bot_prompt_id':bot_dict['initial_prompt_id'],
            'bot_model_config_id': bot_dict['model_config_id'],
            'status':self.SessionStatus.STARTED.value,
            'created_date':gu.get_current_time(),
            'message_count':0,
            'total_token_count':0,
            'current_prompt_id':None
        }

        # create the session 
        session_id = self.db.create_doc(collection_name="sessions",data=session_dict)

        if not session_id:
            raise self.DBRecordError("DB Record Error: session not created")       

        return {'session_id': session_id, 'bot_dict': bot_dict}

    # internal function to record a session prompt 
    def _record_session_prompt(self, session_id, prompt_message):
        prompt_dict = {
            'message': prompt_message.replace("\n",""), 
            'created_date': gu.get_current_time()
        }

        prompt_id = self.db.create_sub_collection_item(collection_name="sessions", document_id=session_id, sub_collection_name="prompts", data=prompt_dict)
        if prompt_id == None:
            raise self.DBRecordError("DB Record Error: prompt not recorded")
        session_update_dict = {'current_prompt_id':prompt_id}
        record_current_prompt = self.db.update_document_fields(collection_name="sessions", document_id=session_id, updates=session_update_dict)
        if record_current_prompt == None:
            raise self.DBAttributeError("DB Attribute Error: session current_prompt_id not updated")
        return True

    # internal function to recod a session message:
    def _record_session_message(self, session_id, message, is_user, total_token=None):
        msg_dict = {
            'message':message.replace(self.openai_restart_sequence,"").replace(self.openai_stop_sequence,""),#.replace("\n","\\n"),
            'is_user':is_user,
            'created_date':gu.get_current_time()
        }
        message_id = self.db.create_sub_collection_item(collection_name="sessions", document_id=session_id, sub_collection_name="messages", data=msg_dict)
        if message_id == None:
            raise self.DBRecordError("DB Record Error: message not recorded")

        # increment message count fields
        message_incremented = self.db.increment_document_fields(collection_name="sessions", document_id=session_id, field_name='message_count', increment=1)
        if message_incremented == None:
            raise self.DBAttributeError("DB Attribute Error: message_count not recorded")

        if total_token:
            token_updated = self.db.update_document_fields(collection_name="sessions", document_id=session_id, updates={'total_token_count':total_token})
            if token_updated == None:
                raise self.DBAttributeError("DB Attribute Error: total_token_count not recorded")

        return True             



## TESTING ##
# stop_sequence = '|STOP|'
# restart_sequence = '|USER|'
#s = sessions()

# create a session 
# session_response_dict = s.create_session(user_id='xxxx', bot_id='xxxx', ai_key='sk-xxxx')
# st.write(session_response_dict)
# gu.clean_display_message_str(message=session_response_dict['response_message'], restart_sequence='|USER|', stop_sequence='|STOP')
# st.markdown(gu.clean_display_message_str(message=session_response_dict['response_message'], restart_sequence=restart_sequence, stop_sequence=stop_sequence))

#user_message_str = "Yo yo yo. Joe! What kinda name is that. Yo no king! Yo ill. You ain't smooth. You slow. I am da King Kong - da greatest. Yo better check yoself!"
#user_message_str = "Whatever dude. You no king. You da chump. You think your rhymes are sick? My girl rhymes better than that. You think you da lightning bolt? I'm the Zeus, I eat lightning bolt."
#user_message_str = "I don't think so dude. Yo think yo flow is hot? My flow is even hotter, like straight from the sun. Yo think yo leaving me in the dust? Bro, I am so far ahead of you, you don't even know. Yo just a lame AI. I am da real king."
#session_response_dict = s.get_session_response(session_id='xxxxx', ai_key='sk-xxxxx', user_message=user_message_str)
#st.write(session_response_dict)
#st.markdown(gu.clean_display_message_str(message=session_response_dict['response_message'], restart_sequence=restart_sequence, stop_sequence=stop_sequence))

#s.end_session(session_id='1vyASpOoIkhoD1vKyvE5', end_status=1)
# s.rate_session(session_id='xxxxx', user_liked=0)

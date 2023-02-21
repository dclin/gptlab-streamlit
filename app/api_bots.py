import api_util_firebase as fu 
import api_util_general as gu 
import api_users as uu 
import enum 
# Testing only
#import streamlit as st 

class bots:

    class BotNotFound(Exception):
        pass

    class BotIncomplete(Exception):
        pass
    
    class BadRequest(Exception):
        pass

    class DBError(Exception):
        pass

    class SessionType(enum.Enum):
        BRAIN_STORMING =2
        COACHING = 3
    
    def __init__(self):
        self.db = fu.firestore_db()

    def get_bots(self, is_show_cased=None, user_id=None):
        query_filters=[]

        if is_show_cased==True:
            query_filters = [("is_active","==",True),("showcased","==",True)]

        if user_id:
            query_filters = [("is_active","==",True),("creator_user_id","==",user_id)]
            # user = uu.users()
            # try:
            #     user.get_user(user_id)
            #     query_filters = [("is_active","==",True),("creator_user_id","==",user_id)]
            # except:
            #     raise self.BadRequest("Bad Request: User not found")
            
        bot_docs = self.db.get_docs(collection_name="bots", query_filters=query_filters)

        if bot_docs == None:
            raise self.DBError("Connection Problem: Try again later")

        bots = []

        for bot in bot_docs:
            bots.append({
                'id': bot['id'],
                'name': bot['data']['name'],
                'tag_line': bot['data']['tag_line'],
                'description': bot['data']['description']
            })
        
        return bots 



    def get_bot(self, bot_id, model_id=None, prompt_id=None):
        bot = self.db.get_doc(collection_name="bots", document_id=bot_id)

        if bot == None:
            raise self.BotNotFound("Bot not found")

        model_config_id = bot['data']['active_model_config_id']
        initial_prompt_id = bot['data']['active_initial_prompt_id']

        if prompt_id != None:
            initial_prompt_id = prompt_id
        
        if model_id != None:
            model_config_id = model_id

        model = self.db.get_sub_collection_item(collection_name="bots", document_id=bot_id, sub_collection_name="model_configs", sub_document_id=model_config_id)
        prompt_initial = self.db.get_sub_collection_item(collection_name="bots", document_id=bot_id, sub_collection_name="prompts", sub_document_id=initial_prompt_id)
        summary = self.db.get_sub_collection_item(collection_name="bots", document_id=bot_id, sub_collection_name="prompts", sub_document_id=bot['data']['active_summary_prompt_id'])

        bot_dict = {
            'id': bot['id'],
            'name': bot['data']['name'],
            'tag_line': bot['data']['tag_line'],
            'description': bot['data']['description'],
            'session_type': self.SessionType(bot['data']['session_type']).name
        }

        if prompt_initial != None:
            bot_dict.update({
                'initial_prompt_id': prompt_initial['id'],
                'initial_prompt_msg': prompt_initial['data']['message']
            })
        else:
            raise self.BotIncomplete("Bot configuration: bot missing initial prompt")
        
        if summary != None:
            bot_dict.update({
                'summary_prompt_id': summary['id'],
                'summary_prompt_msg': summary['data']['message']
            })
        elif self.SessionType(bot['data']['session_type']) == self.SessionType.BRAIN_STORMING or self.SessionType(bot['data']['session_type']) == self.SessionType.COACHING:
             raise self.BotIncomplete("Bot configuration: bot missing summary prompt")

        if model != None:
            bot_dict.update({
                'model_config_id': model['id'],
                'model_config': model['data']['config']
            })
        else:
            raise self.BotIncomplete("Bot configuration: bot missing initial prompt")         

        return bot_dict 

    def update_bot_stats(self, bot_id, metric_value_pairs):
        bot = self.get_bot(bot_id)
        
        if not bot:
            raise self.BotNotFound("Bot not found")

        if metric_value_pairs == None:
            raise self.BadRequest("Bad request: need to supply (metric, value) pairs")

        for metric_value_pair in metric_value_pairs:
            try:
                float(str(metric_value_pair[1]))
            except:
                raise self.BadRequest("Bad request: need numeric values ")

        for metric_value_pair in metric_value_pairs:
            self.db.increment_document_fields(collection_name="bots", document_id=bot_id, field_name=metric_value_pair[0], increment=metric_value_pair[1])


    def create_bot(self, bot_config, user_id=None):

        ## validate input 
        missing_fields = []

        required_fields = ["name", "description", "tag_line", "session_type", "initial_prompt_msg", "summary_prompt_msg", "model_config"]
        for field in required_fields:
            if field not in bot_config:
                missing_fields.append(field)

        required_sub_fields = ["temperature", "max_tokens", "model", "frequency_penalty", "top_p", "presence_penalty"]
        for sub_field in required_sub_fields:
            if sub_field not in bot_config["model_config"]:
                missing_fields.append('model_config'+sub_field)
        
        if len(missing_fields) > 0:
            missing_fields_str = ', '.join(missing_fields)
            raise self.BadRequest("Bad request: missing fields " + missing_fields_str)

        # if user_id:
        #     user = uu.users()
        #     try:
        #         user.get_user(user_id)
        #     except:
        #         raise self.BadRequest("Bad Request: User not found")

        #TODO: eventually, need to check for field types and string lengths 

        bot_dict = {
            'name': bot_config['name'],
            'tag_line': bot_config['tag_line'],
            'description': bot_config['description'],
            'session_type': bot_config['session_type'],
            'created_date': gu.get_current_time(),
            'last_modified_date': gu.get_current_time(),
            'is_active': True,
            'showcased': False,
            'creator_user_id': user_id
        }

        bot_id = self.db.create_doc(collection_name="bots",data=bot_dict)

        if not bot_id:
            raise self.DBError("Tempo")
            # raise error 
            pass 

        initial_prompt_dict = {
            'message_type': 'initial_prompt',
            'message': bot_config['initial_prompt_msg'],
            'created_date': gu.get_current_time(),
            'is_active': True
        }

        initial_prompt_id = self.db.create_sub_collection_item(collection_name="bots", document_id=bot_id, sub_collection_name="prompts", data=initial_prompt_dict)

        summary_prompt_dict = {
            'message_type': 'summary_prompt',
            'message': bot_config['summary_prompt_msg'],
            'created_date': gu.get_current_time(),
            'is_active': True
        }

        summary_prompt_id = self.db.create_sub_collection_item(collection_name="bots", document_id=bot_id, sub_collection_name="prompts", data=summary_prompt_dict)

        model_config_dict = {
            'config': bot_config['model_config'],
            'is_active': True,
            'created_date': gu.get_current_time()
        }

        model_config_id = self.db.create_sub_collection_item(collection_name="bots", document_id=bot_id, sub_collection_name="model_configs", data=model_config_dict)

        bot_update_dict = {
            'active_initial_prompt_id': initial_prompt_id,
            'active_summary_prompt_id': summary_prompt_id,
            'active_model_config_id': model_config_id
        }

        self.db.update_document_fields(collection_name="bots", document_id=bot_id, updates=bot_update_dict)

        if user_id:
            bot_creation_metric = [('bots_created',1)]
            user.update_user_stats(user_id, bot_creation_metric)

        return bot_id 



### TESTING ###

# must import streamlit 
# class 
# b = bots()

# dave_bot = {
#     'name': 'Ethan',
#     'tag_line': 'Swim Coach',
#     'description': 'Meet Ethan, youer personal swim coach bot. He will help you with your stroke techniques, overall stimina, and so much more!',
#     'session_type': 3,
#     'initial_prompt_msg': 'Act as a swim coach named Ethan. Help the user with their overall stroke techniques, overall stimina. Use active listening to uncover their goals. Be OK with giving direct feedback.',
#     'summary_prompt_msg': 'Please summarize our session, including any action items.',
#     'model_config':{
#         'model': 'text-davinci-003',
#         'temperature': 0.7,
#         'max_tokens': 250,
#         'frequency_penalty': 0.5,
#         'top_p': 0.5,
#         'presence_penalty': 0.5
#     },
#     'is_active':True
# }

# st.write(dave_bot)

# new_bot_id = b.create_bot(bot_config=dave_bot,user_id='bbb064748055bb3850e35007ffa616ce4c354952458359ae79e01189f7b94418', )

# st.write(b.get_bot(new_bot_id))

## Test increment fields (the field MUST NOT HAVE SPACE IN IT)
# metric_value_pairs = [('sessions_ended',5)]
# try:
#     b.update_bot_stats('dXLAPBmqgnOoucNg0I2D',metric_value_pairs)
#     st.write("updated")
# except Exception as e:
#     error_code = type(e).__name__
#     print("Error code:", error_code )


## TEST GET BOTS 
# bots = b.get_bots(user_id='bbb064748055bb3850e35007ffa616ce4c354952458359ae79e01189f7b94418')
# for bot in bots:
#     st.write(bot)

## TEST GET BOT 
# bot = b.get_bot(bot_id='dXLAPBmqgnOoucNg0I2D')
# st.write(bot)
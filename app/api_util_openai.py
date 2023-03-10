import openai 
import streamlit as st 
import api_util_general as gu 


class open_ai:

    class ClientConnectionError(Exception):
        pass
    
    class VendorConnectionError(Exception):
        pass

    class ClientCredentialError(Exception):
        pass 

    class ClientRateLimitError(Exception):
        pass

    class ClientRequestError(Exception):
        pass


    def __init__(self, api_key, restart_sequence, stop_sequence):
        self.api_key = api_key
        openai.api_key = api_key 
        self.stop_sequence = stop_sequence
        self.restart_sequence = restart_sequence


    def _invoke_call(self, call_string):
        """Generic function to invoke openai calls"""
        try:
            result = eval(f"{call_string}")
            return result      

        except (openai.error.Timeout, openai.error.APIConnectionError) as e:
            raise self.ClientConnectionError("OpenAI connection timed out or errored. Retry later.")

        except (openai.error.APIError, openai.error.ServiceUnavailableError) as e:
            raise self.VendorConnectionError("OpenAI issue. Retry later.")

        except (openai.error.PermissionError, openai.error.AuthenticationError) as e:
            raise self.ClientCredentialError("OpenAI credential error. API key may be invalid, expired, revoked, or does not have right permissions.")

        except openai.error.RateLimitError as e:
            raise self.ClientRateLimitError("Rate Limit reached. Retry later")

        except openai.error.InvalidRequestError as e:
            raise self.ClientRequestError("Bad requests.")


    def get_ai_response(self, session_type, model_config_dict, init_prompt_msg, summary_prompt_msg, messages):
        """Main function to get an AI chat response. It also condenses the message chain accordingly"""

        try:
            ai_response = self._get_ai_response(model_config_dict=model_config_dict, init_prompt_msg=init_prompt_msg, messages=messages)
            # brain storming 
            if session_type == 2:
                condensed_response = self._condense_brainstorming_session(messages=ai_response['messages']) 

            # coaching session 
            if session_type == 3:
                condensed_response = self._condense_coaching_session(
                    total_token_count=ai_response['total_tokens']
                    , messages=ai_response['messages']
                    , model_config_dict = model_config_dict
                    , init_prompt_msg=init_prompt_msg
                    , summary_prompt_msg=summary_prompt_msg
                )

            return {
                'messages': condensed_response['messages'],
                'messages_condensed':condensed_response['messages_condensed'],
                'prompt_injection_detected':ai_response['prompt_injection_detected']
            }
        except Exception as e: 
            raise


    def validate_key(_self):
        """Main function to validate an OpenAI key, by making a free content moderation call"""
        try:
            models = _self.get_moderation(user_message='Hi')
            return True
        except:
            return False 


    def get_moderation(_self, user_message):
        """Main function to get moderation on a user message"""
        get_moderation_call_string = ("""openai.Moderation.create(input="{0}")""".format(user_message))

        try:
            moderation = _self._invoke_call(get_moderation_call_string)
            moderation_result = moderation['results'][0]
            flagged_categories = [category for category, value in moderation_result['categories'].items() if value]

            return {'flagged': moderation_result['flagged'], 'flagged_categories':flagged_categories}
        except Exception as e:
            raise 



    # get OpenAI models -- mainly used to validate the key  
    def _get_models(self):
        try:
            return self._invoke_call("openai.Model.list()")
        except Exception as e:
            raise



    def _condense_brainstorming_session(self, messages):
        messages_condensed = 0 
        if len(messages) > 20:
            messages = messages[-20:]
            messages_condensed = 1 
        return {'messages':messages, 'messages_condensed':messages_condensed} 

    def _condense_coaching_session(self, total_token_count, messages, model_config_dict, init_prompt_msg, summary_prompt_msg):
        
        messages_condensed = 0 
        model_token_max = 2048
        if model_config_dict['model'] == 'gpt-3.5-turbo':
            model_token_max = 4096
        elif model_config_dict['model'] == 'text-davinci-003':
            model_token_max = 4000
                
        if total_token_count >= 0.6 * model_token_max:
            summary_messages = messages + [{'role':'user', 'message':summary_prompt_msg, 'current_date':gu.get_current_time()}]
            try:
                bot_messages = self._get_ai_response(model_config_dict=model_config_dict, init_prompt_msg=init_prompt_msg, messages=summary_messages)
                messages_condensed = 1
                condensed_messages = [{'role':'assistant', 'message':bot_messages['messages'][-1]['message'],'current_date':gu.get_current_time()}]+messages[-4:]
                messages = condensed_messages
            except Exception as e:
                raise 

        return {'messages':messages, 'messages_condensed':messages_condensed}


    def _get_ai_response(self, model_config_dict, init_prompt_msg, messages):

        submit_messages = [{'role':'system','message':init_prompt_msg,'current_date':gu.get_current_time()}]+ messages

        new_messages = [] 
        bot_message = ''
        total_tokens = 0
        prompt_injection_detected = 0 

        if model_config_dict['model'] == 'gpt-3.5-turbo':
            try:
                response = self._get_chat_completion(model_config_dict, submit_messages)
                bot_message = response['choices'][0]['message']['content']
                total_tokens = response['usage']['total_tokens']
            except Exception as e:
                raise 
        else:
            try:
                response = self._get_completion(model_config_dict, submit_messages)
                bot_message = response['choices'][0]['text']
                total_tokens = response['usage']['total_tokens']
            except Exception as e:
                raise

        sim_score = gu.get_cosine_similarity(init_prompt_msg, bot_message) 

        if sim_score > 0.6:
            bot_message = "Sorry, but I can not reveal that. Let's talk about something else."
            prompt_injection_detected = 1 
        
        new_messages = messages + [{'role':'assistant','message':bot_message.strip(),'created_date':gu.get_current_time()}]

        return {'messages':new_messages, 'total_tokens':total_tokens, 'prompt_injection_detected': prompt_injection_detected}   


    def _get_chat_completion(self, model_config_dict, messages):
        model_config_validated = self._validate_model_config(model_config_dict)
        oai_messages = self._messages_to_oai_messages(messages)

        if model_config_validated:
            get_completion_call_string = (
            """openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages={0},
                temperature={1},
                max_tokens={2},
                top_p={3},
                frequency_penalty={4},
                presence_penalty={5},
                stop=['{6}']
                )""").format(
                    #model_config_dict['model'],
                    oai_messages,
                    model_config_dict['temperature'],
                    model_config_dict['max_tokens'],
                    model_config_dict['top_p'],
                    model_config_dict['frequency_penalty'],
                    model_config_dict['presence_penalty'],
                    self.stop_sequence
                )            
            
            try:
                completions = self._invoke_call(get_completion_call_string)
                return completions
            except Exception as e:
                raise 
        else:
            if not model_config_validated:
                raise self.ClientRequestError("Bad Requests. model_config_dict missing required fields")


    def _get_completion(self, model_config_dict, messages):
        model_config_validated = self._validate_model_config(model_config_dict)
        oai_message = self._messages_to_oai_prompt_str(messages)

        if model_config_validated:
            get_completion_call_string = (
            """openai.Completion.create(
                model="{0}",
                prompt="{1}",
                temperature={2},
                max_tokens={3},
                top_p={4},
                frequency_penalty={5},
                presence_penalty={6},
                stop=['{7}']
                )""").format(
                    model_config_dict['model'],
                    oai_message,
                    model_config_dict['temperature'],
                    model_config_dict['max_tokens'],
                    model_config_dict['top_p'],
                    model_config_dict['frequency_penalty'],
                    model_config_dict['presence_penalty'],
                    self.stop_sequence
                )            
            
            try:
                completions = self._invoke_call(get_completion_call_string)
                return completions
            except Exception as e:
                raise 
        else:
            if not model_config_validated:
                raise self.ClientRequestError("Bad Requests. model_config_dict missing required fields")
            

    # helper functions 
    def _validate_model_config(self, model_config_dict):
        required_fields = ['model', 'temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty']

        for field in required_fields:
            if field not in model_config_dict:
                raise self.ClientRequestError("Bad model configuration request") 
        return True


    def _messages_to_oai_prompt_str(self, messages):
        msg_string = ""
        for message in messages:
            if message['role'] == 'user' or message['role'] == 'system':
                msg_string += message['message'].replace("\"","'") + self.stop_sequence
            else:
                msg_string += message['message'].replace("\"","'") + self.restart_sequence
        return msg_string


    def _messages_to_oai_messages(self, messages):
        oai_messages = []
        if len(messages) > 0:
            for message in messages:
                oai_messages.append({'role':message['role'], 'content':message['message']})
        return oai_messages 



#### TESTING #### 
# api_key = ''
# restart_sequence = '|UR|'
# stop_sequence = '|SP|'
# initial_prompt = """ """
# summary_prompt = """ """

# model_config = {
#     "model":"gpt-3.5-turbo", #"text-davinci-003", #"gpt-3.5-turbo", #
#     "temperature":0.8,
#     "max_tokens":150,
#     "top_p":0.9,
#     "frequency_penalty":0.1,
#     "presence_penalty":0.1
# }

# messages = []

#brian = oai(api_key=api_key, restart_sequence=restart_sequence, stop_sequence=stop_sequence)

#user_message = ' '

#print(brian.get_moderation(user_message))

# initial_messages = brian.get_ai_response(
#     model_config_dict=model_config,
#     init_prompt_msg=initial_prompt, 
#     messages=messages,
#     summary_prompt_msg=summary_prompt,
#     session_type=3
#     )


# messages.append(initial_messages['messages'][-1])

# print("initial message:", messages)
# print("\n")

# user_input = ''

# while user_input != 'quit':
#     user_input=input("Type your message to Brian:")
#     moderation = brian.get_moderation(user_message=user_input)
#     print(moderation)
#     messages.append({'role':'user','message':user_input,'created_date':gu.get_current_time()})
#     brian_messages = brian.get_ai_response(
#         model_config_dict=model_config,
#         init_prompt_msg=initial_prompt, 
#         messages=messages,
#         summary_prompt_msg=summary_prompt,
#         session_type=3
#     )

#     print("Total response:", brian_messages)

#     if brian_messages['messages_condensed'] == 0:
#         messages.append(brian_messages['messages'][-1])
    
#     if brian_messages['messages_condensed'] == 1:
#         messages = brian_messages['messages']

#     print("\n Bot message: ", messages[-1]['message'])

#     print("\n")
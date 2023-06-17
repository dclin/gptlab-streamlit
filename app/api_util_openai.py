import openai 
import streamlit as st 
import api_util_general as gu 
import time 
import sys 


class open_ai:

    class OpenAIError(Exception):
        def __init__(self, message, error_type=None):
            super().__init__(message)
            self.error_type = error_type 

    def __init__(self, api_key, restart_sequence, stop_sequence):
        self.api_key = api_key
        openai.api_key = api_key 
        self.stop_sequence = stop_sequence
        self.restart_sequence = restart_sequence


    def _invoke_call(self, call_string, max_tries=3, initial_backoff=1):
        """Generic function to invoke openai calls"""
        RETRY_EXCEPTIONS = (
            openai.error.APIError, 
            openai.error.Timeout, 
            openai.error.APIConnectionError, 
            openai.error.ServiceUnavailableError
        )
        tries = 0
        backoff = initial_backoff

        while True: 
            try:
                result = eval(f"{call_string}")
                return result     

            except Exception as e:
                if isinstance(e, RETRY_EXCEPTIONS) and tries < max_tries:
                    time.sleep(backoff)
                    backoff *= 2
                    tries +=1
                else:
                    raise self.OpenAIError(f"OpenAI: {str(e)}", error_type=type(e).__name__) from e 

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


    def validate_key(self):
        """Main function to validate an OpenAI key, by making a free content moderation call"""
        try:
            models = self._get_models()
            models_list = [model.id for model in models['data']]
            gpt_lab_models_list = ['gpt-4-32k','gpt-4','gpt-3.5-turbo-16k', 'gpt-3.5-turbo', 'text-davinci-003', 'text-curie-001', 'text-babbage-001', 'text-ada-001']
            key_supported_models_list = [model for model in gpt_lab_models_list if model in models_list] 
            #print(key_supported_models_list)
            return {'validated': True, 'supported_models_list': key_supported_models_list}
        except Exception as e:
            raise


    def get_moderation(self, user_message):
        """Main function to get moderation on a user message"""
        get_moderation_call_string = ("""openai.Moderation.create(input="{0}")""".format(user_message))

        try:
            moderation = self._invoke_call(get_moderation_call_string)
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
        model_token_max = 2049
        if model_config_dict['model'] == 'gpt-4-32k':
            model_token_max = 32768
        elif model_config_dict['model'] == 'gpt-4':
            model_token_max = 8192
        elif model_config_dict['model'] == 'gpt-3.5-turbo-16k':
            model_token_max = 16384
        elif model_config_dict['model'] in ('gpt-3.5-turbo', 'text-davinci-003'):
            model_token_max = 4096
                
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

        if model_config_dict['model'] in ('gpt-3.5-turbo', 'gpt-3.5-turbo-16k', 'gpt-4', 'gpt-4-32k'):
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
                model="{0}",
                messages={1},
                temperature={2},
                max_tokens={3},
                top_p={4},
                frequency_penalty={5},
                presence_penalty={6},
                stop=['{7}']
                )""").format(
                    model_config_dict['model'],
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



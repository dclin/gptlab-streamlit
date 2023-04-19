import streamlit as st
import api_users as au 

legal_prompt = "Ready to explore the endless possibilities of AI? Review and agree to our Terms of Use and Privacy Policy, available on our Terms page. By signing in, you confirm that you have read and agreed to our policies. Let's get started today!"
user_key_prompt = "Enter your OpenAI API key to get started. Keep it safe, as it'll be your key to coming back. \n\n**Friendly reminder:** GPT Lab works best with pay-as-you-go API keys. Free trial API keys are limited to 3 requests a minute, not enough to chat with assistants. For more information on OpenAI API rate limits, check [this link](https://platform.openai.com/docs/guides/rate-limits/overview).\n\n- Don't have an API key? No worries! Create one [here](https://platform.openai.com/account/api-keys).\n- Want to upgrade your free-trial API key? Just enter your billing information [here](https://platform.openai.com/account/billing/overview)."
user_key_failed = "You entered an invalid OpenAI API key."
user_key_success = "Thanks for signing in! Make sure to keep the OpenAI API key safe, as it'll be your key to coming back. Happy building!"
api_key_placeholder = "Paste your OpenAI API key here (sk-...)"


class app_user:
    def __init__(self):
        if 'user' not in st.session_state:
            st.session_state.user = {'id':None, 'api_key':None, 'user_hash': None, 'key_supported_models_list':[]}
        if 'user_validated' not in st.session_state:
            st.session_state.user_validated = None 
        self.container = st.container()
        
    def _get_info(self):
        return st.session_state.user 

    def _set_info(self, user_id, api_key, user_hash, key_supported_models_list):
        st.session_state.user = {'id': user_id, 'api_key': api_key, 'user_hash' : user_hash, 'key_supported_models_list': key_supported_models_list}

    def view_get_info(self):
        with self.container:
            st.markdown(legal_prompt)
            st.markdown("\n")
            st.info(user_key_prompt)
            st.text_input("Enter your OpenAI API Key", key="user_key_input",on_change=self._validate_user_info, type="password", autocomplete="current-password", placeholder=api_key_placeholder)

    def _validate_user_info(self):
        u = au.users()

        try:
            user = u.get_create_user(api_key=st.session_state.user_key_input)           
            self._set_info(user_id=user['id'], api_key = st.session_state.user_key_input, user_hash=user['data']['user_hash'], key_supported_models_list=user['data']['supported_models_list'])
            st.session_state.user_validated = 1 
        except u.OpenAIError as e: 
            with self.container:
                st.error(f"{str(e)}")
        except u.DBError as e:
            with self.container:
                st.warning("Something went wrong. Please try again.")      

    def view_success_confirmation(self):
        st.write(user_key_success)


if __name__ == '__main__':
    vu = app_user()
    if 'user_validated' not in st.session_state or st.session_state.user_validated != 1:
        vu.view_get_info()
    else:
        vu.view_success_confirmation()

# st.write(st.session_state)
import streamlit as st
import streamlit.components.v1 as c 
import api_users as au 

legal_prompt = "If you have not done so, please review and agree to our Terms of Use and Privacy Policy, both of which are available on the Terms page. By signing in, you confirm that you have read and agreed to the Terms of Use and Privacy Policy."
user_key_prompt = "Enter your OpenAI API key to get started. Keep it safe, as it'll be your key to coming back.  \nDon't have one yet? Create one at: https://platform.openai.com/account/api-keys."
user_key_failed = "You entered an invalid OpenAI API key."
user_key_success = "Thanks for signing in! Make sure to keep the OpenAI API key safe, as it'll be your key to coming back. Happy building!"


class app_user:
    def __init__(self):
        if 'user' not in st.session_state:
            st.session_state.user = {'id':None, 'api_key':None}
        if 'user_validated' not in st.session_state:
            st.session_state.user_validated = None 
        self.container = st.container()
        
    def _get_info(self):
        return st.session_state.user 

    def _set_info(self, user_id, api_key, user_hash):
        st.session_state.user = {'id': user_id, 'api_key': api_key, 'user_hash' : user_hash}

    def view_get_info(self):
        with self.container:
            st.markdown(legal_prompt)
            st.markdown("\n")
            st.info(user_key_prompt)
            st.text_input("Enter your OpenAI API Key", key="user_key_input",on_change=self._validate_user_info, type="password", autocomplete="current-password")

    def _validate_user_info(self):
        u = au.users()

        try:
            user = u.get_create_user(api_key=st.session_state.user_key_input)           
            self._set_info(user_id=user['id'], api_key = st.session_state.user_key_input, user_hash=user['data']['user_hash'])
            st.session_state.user_validated = 1 
        except u.OpenAIClientCredentialError as e:
            with self.container:
                st.error(user_key_failed)
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
import streamlit as st 

# class for the reusable chat component 
class app_chat: 

    def __init__(self, bot_name, bot_tag_line):
        self.input_container = st.container()
        self.chat_container = st.container()
        self.bot_name = bot_name 
        self.bot_tag_line = bot_tag_line
        self.bot_avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}&radius=25".format(bot_name) 
        self.user_avatar_url = 'https://api.dicebear.com/5.x/avataaars-neutral/svg?seed=ARoN&radius=25&backgroundColor=f8d25c'

    def render_chat_session(self, message_list, handler_user_chat, handler_session_end=None):
            st.write("\n")
            self._render_user_input(handler_user_chat=handler_user_chat, handler_session_end=handler_session_end)
            self._render_chat_histories(message_list=message_list)


    def get_user_input_variable_str(self):
        return "{0}_user_chat_input".format(self.bot_name)

    def _render_user_input(self, handler_user_chat, handler_session_end=None):
        with self.input_container:
            col1, col2 = st.columns([4, 1])

            with col1:
                st.text_input(
                    "Talk to {0}".format(self.bot_name), 
                    key = self.get_user_input_variable_str(), 
                    on_change=handler_user_chat
                )

            if handler_session_end != None:
                with col2:
                    st.text("")
                    st.text("")
                    st.button("End Session",
                    key = "end_session",
                    on_click=handler_session_end 
                    )
            
            st.markdown("""---""")


    def _render_chat_histories(self, message_list):
        with self.chat_container:
            for i in range(len(message_list)-1,-1,-1):
                self._render_message(message_list[i]['is_user'], message_list[i]['message'])


    def _render_message(self, is_user, message):
        avatar_url = self.user_avatar_url

        if is_user == False:
            avatar_url = self.bot_avatar_url 

        col1, col2 = st.columns([1,5], gap="small")
        col1.image(avatar_url, width=50)
        col2.markdown(message)
        st.write("\n")



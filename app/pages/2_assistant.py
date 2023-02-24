import streamlit as st 
import app_user as vuser
import app_utils as vutil
import app_component as ac 
import api_bots as abots 
import api_sessions as asessions 

st.set_page_config(
    page_title="GPT Lab - Assistant",
    page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"#,
    #menu_items={"About": "GPT Lab is a user-friendly app that allows anyone to interact with and create their own AI Assistants powered by OpenAI's GPT-3 language model. Our goal is to make AI accessible and easy to use for everyone, so you can focus on designing your Assistant without worrying about the underlying infrastructure.", "Get help": None, "Report a Bug": None}
)


st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)

def handler_bot_search(search_container=None, user_search_str=None):
    if user_search_str == None:
        user_search_str = st.session_state.bot_search_input
    try:
        b = abots.bots()
        bot = b.get_bot(user_search_str)
        st.session_state.bot_info = bot 
        st.session_state.bot_validated = 1 
        return True 
    except b.BotNotFound as e: 
        if search_container:
            with search_container: 
                st.error("AI assistant could not be found")
        # else:
        #     st.error("AI assistant could not be found")
        return False 
    except b.BotIncomplete as e:
        if search_container:
            with search_container:
                st.error("AI assistant could not be selected, as it was not configured properly.")
        # else:
        #     st.error("AI assistant could not be selected, as it was not configured properly.")
        return False 

def handler_start_session():
    try:
        s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])
        chat_session = s.create_session(user_id=st.session_state.user['id'], bot_id=st.session_state.bot_info['id'], ai_key=st.session_state.user['api_key'])
        st.session_state.session_id = chat_session['session_id']
        # Create a session state variables to hold messages 
        st.session_state.session_msg_list = []
        bot_message = chat_session['response_message']
        st.session_state.session_msg_list.append({'is_user':False, 'message':bot_message})
    except s.OpenAIClientCredentialError as e:
        del st.session_state['user']
        st.session_state.user_validated = 0 
        del st.session_state['bot_info']
        st.session_state.bot_validated = 0 
        st.error("Your API credential is no longer valid.")
    except s.BadRequest as e:
        del st.session_state['bot_info']
        st.session_state.bot_validated = 0 
        st.error("Something went wrong. Could not start a session with the AI assistant. Please try again later.")
    except s.SessionNotRecorded as e:
        del st.session_state['bot_info']
        st.session_state.bot_validated = 0 
        st.error("Could not start a session with the AI assistant. Please try again later.")
    except s.OpenAIConnectionError as e:
        del st.session_state['bot_info']
        st.session_state.bot_validated = 0 
        st.error("Could not start a session with the AI assistant. OpenAI is experiencing some technical difficulties.")
    except s.OpenAIClientRateLimitError as e:
        del st.session_state['bot_info']
        st.session_state.bot_validated = 0 
        st.error("Could not start a session with the AI assistant. Exceeded OpenAI rate limit. Please try again later.")
    except s.OpenAIClientConnectionError as e:
        del st.session_state['bot_info']
        st.session_state.bot_validated = 0 
        st.error("Could not start a session with the AI assistant. Could not establish connection with OpenAI. Please try again later.")
    except s.PromptNotRecorded as e:
        del st.session_state['bot_info']
        st.session_state.bot_validated = 0 
        st.error("Session creation incomplete. Could not record AI response. Please try again later.")
    except s.MessageNotRecorded as e:
        del st.session_state['bot_info']
        st.session_state.bot_validated = 0 
        st.error("Session creation incomplete. Could not record AI response. Please try again later.")


def handler_user_chat():
    user_message = st.session_state.user_chat_input.replace("\n","")
    st.session_state.session_msg_list.append({"message":user_message, "is_user": True})

    s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])
    try:
        session_response = s.get_session_response(st.session_state.session_id, st.session_state.user['api_key'], user_message=user_message)
        if session_response:
            st.session_state.session_msg_list.append({"message":session_response['response_message'], "is_user": False})
        st.session_state.user_chat_input= "" # clearing text box 
    except s.BadRequest as e:
        del st.session_state['bot_info']
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Try again later.")
    except s.OpenAIClientCredentialError as e:
        del st.session_state['user']
        st.session_state.user_validated = 0 
        del st.session_state['bot_info']
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Your API credential is no longer valid.")
    except s.OpenAIConnectionError as e:
        del st.session_state['bot_info']
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Could not establish connection with OpenAI. Try again later.")
    except s.OpenAIClientRateLimitError as e:
        del st.session_state['bot_info']
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Exceeded OpenAI rate limit. Try again later.")
    except s.SessionAttributeNotUpdated as e:
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Try again later.")
    except s.PromptNotRecorded as e:
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Try again later.")
    except s.MessageNotRecorded as e: 
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Try again later.")
    except Exception as e: 
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Unknown error. Try again later.")




def handler_session_end():
    s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])
    try:
        session_response = s.get_session_response(st.session_state.session_id, st.session_state.user['api_key'], user_message=st.session_state.bot_info['summary_prompt_msg'])
        if session_response:
            st.session_state.session_msg_list.append({"message":session_response['response_message'], "is_user": False})
    except s.BadRequest as e:
        del st.session_state['bot_info']
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Try again later.")
    except s.OpenAIClientCredentialError as e:
        del st.session_state['user']
        st.session_state.user_validated = 0 
        del st.session_state['bot_info']
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Your API credential is no longer valid.")
    except s.OpenAIConnectionError as e:
        del st.session_state['bot_info']
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Could not establish connection with OpenAI. Try again later.")
    except s.OpenAIClientRateLimitError as e:
        del st.session_state['bot_info']
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Exceeded OpenAI rate limit. Try again later.")
    except s.SessionAttributeNotUpdated as e:
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Try again later.")
    except s.PromptNotRecorded as e:
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Try again later.")
    except s.MessageNotRecorded as e: 
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Could not get AI response. Try again later.")
    except Exception as e: 
        del st.session_state['session_id']
        st.session_state.bot_validated = 0
        del st.session_state['session_msg_list']
        st.error("Unknown error. Try again later.")
    st.session_state.session_ended = 1 
    st.session_state.user_chat_input= "" # clearing text box 
    try:
        s.end_session(st.session_state['session_id'])
    except Exception as e:
        pass # purposely swallow all sort of exceptions. no point trouble users


def handler_bot_cancellation():
    st.session_state.bot_validated = 0 
    del st.session_state.bot_info 
    url_params = st.experimental_get_query_params()
    if bool(url_params) == True and 'assistant_id' in url_params:
        st.experimental_set_query_params(assistant_id="")



def render_user_login_required():
    st.title("AI Assistant")
    st.write("Chat with an AI Assistant")
    #st.markdown("---")
    ac.robo_avatar_component()
    st.write("\n")
    uu = vuser.app_user()
    uu.view_get_info()


def render_bot_search():
    st.title("AI Assistant")
    st.write("Discover other Assistants in the Lounge, or locate a specific AI Assistant by its personalized code.")
    #st.markdown("---")
    ac.robo_avatar_component()
    st.write("\n")
    search_container = st.container()
    with search_container:
        st.text_input("Locate with a specific AI Assistant by entering its personalized code", key = "bot_search_input", on_change=handler_bot_search, args=(search_container,))
    st.write("or")
    if st.button("Back to Lounge"):
        if "bot_info" in st.session_state:
            del st.session_state['bot_info']
        if "session_id" in st.session_state:
            del st.session_state['session_id']
        st.session_state.session_ended = 0 
        st.session_state_bot_validated = 0
        if "session_msg_list" in st.session_state:
            del st.session_state['session_msg_list']
        vutil.switch_page('lounge')



def render_bot_details(bot):
    title_str = "{0}: AI {1}".format(bot['name'],bot['tag_line'])
    st.title(title_str)
    st.write("\n")
    avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}".format(bot['name'])
    button_label="Start chatting with {0}".format(bot['name'])
    button_key="Bot_Details_{0}".format(bot["id"])
    col1, col2 = st.columns([1, 5])
    col1.image(avatar_url, width=50)
    col2.write(bot['description'])
    st.write("\n")

    col1, col2 = st.columns(2)
    col1.button("Start Session with {0}".format(bot['name']), key = "bot_confirm", on_click=handler_start_session)
    col2.button("Find another AI assistant", key = "bot_cancel", on_click=handler_bot_cancellation)


def render_chat_session():
    title_str = "{0}: AI {1}".format(st.session_state.bot_info['name'],st.session_state.bot_info['tag_line'])
    st.title(title_str)

    if st.session_state.session_ended == 0:
        # input box 
        with st.container():
            col1, col2 = st.columns([4, 1])

            with col1:
                st.text_input(
                    "Talk to {0}".format(st.session_state.bot_info['name']), 
                    key = "user_chat_input",
                    on_change=handler_user_chat
                )

            with col2:
                st.text("")
                st.text("")
                st.button("End Session",
                key = "end_session",
                on_click=handler_session_end 
                )
            
        st.markdown("""___""")
        # Chat module 
        for i in range(len(st.session_state.session_msg_list)-1,-1,-1): # chat in st.session_state.session_msg_list:
            render_message(st.session_state.session_msg_list[i]['is_user'], st.session_state.bot_info['name'], st.session_state.session_msg_list[i]['message'])
    
    if st.session_state.session_ended == 1: 
        st.write("Session Recap")
        message = st.session_state.session_msg_list[-1]['message']
        st.markdown(message.replace("\n","  \n"))
        if st.button("Return to lounge"):
            if "bot_info" in st.session_state:
                del st.session_state['bot_info']
            if "session_id" in st.session_state:
                del st.session_state['session_id']
            st.session_state.session_ended = 0 
            st.session_state.bot_validated = 0
            if "session_msg_list" in st.session_state:
                del st.session_state['session_msg_list']
            vutil.switch_page('lounge')


def render_message(is_user, bot_name, message):
    avatar_url = "https://api.dicebear.com/5.x/avataaars-neutral/svg?seed=ARoN&radius=25&backgroundColor=f8d25c"

    if is_user == False:
        avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}&radius=25".format(bot_name) 

    col1, col2 = st.columns([1, 5], gap="small")
    #col1, col2, col3 = st.columns([1, 5, 1], gap="small")
    col1.image(avatar_url, width=50)
    col2.markdown(message.replace("\n","  \n"))
    # if is_user == True:
    #     col3.image(avatar_url, width=50)
    # else:
    #     col1.image(avatar_url, width=50)

    st.write("\n")



## STATE MANAGEMENT

if "user_validated" not in st.session_state:
    st.session_state.user_validated = 0

if "bot_validated" not in st.session_state:
    st.session_state.bot_validated = 0

if "session_ended" not in st.session_state:
    st.session_state.session_ended = 0 

if st.session_state.user_validated != 1:
    render_user_login_required()

# "bot_id" does not exist in session_state
if st.session_state.user_validated == 1 and st.session_state.bot_validated == 0:

    url_params = st.experimental_get_query_params()
    if bool(url_params) == True and 'assistant_id' in url_params:
        if url_params['assistant_id'][0] != "":
            bot_found = handler_bot_search(user_search_str=url_params['assistant_id'][0])
            if bot_found == False:
                st.error("Assistant in URL cannot be found")
                st.experimental_set_query_params(assistant_id="")
                render_bot_search() 
    else:
        render_bot_search()

if st.session_state.user_validated == 1 and st.session_state.bot_validated == 1 and "session_id" not in st.session_state:
    if "initial_summary_prompt_msg" in st.session_state.bot_info:
        render_bot_details(st.session_state.bot_info)    
    else:
        handler_bot_search(user_search_str=st.session_state.bot_info['id'])
        render_bot_details(st.session_state.bot_info)    


if st.session_state.user_validated == 1 and st.session_state.bot_validated == 1 and "session_id" in st.session_state:
    render_chat_session()

#st.write(st.session_state)
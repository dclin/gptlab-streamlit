import streamlit as st 
import app_user as vuser
import app_utils as vutil
import app_component as ac 
import api_bots as abots 
import api_sessions as asessions 
import api_util_general as ag 
import csv 
import io 

st.set_page_config(
    page_title="GPT Lab - Assistant",
    page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"
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
        return False 
    except b.BotIncomplete as e:
        if search_container:
            with search_container:
                st.error("AI assistant could not be selected, as it was not configured properly.")
        return False 

def handler_start_session():

    def _cleanup_handler_start_session_exception():
        if "bot_info" in st.session_state:
            del st.session_state['bot_info']
        if "session_id" in st.session_state:
            del st.session_state['session_id']
        if "session_bot_id" in st.session_state:
            del st.session_state['session_bot_id']
        if "session_msg_list" in st.session_state:
            del st.session_state['session_msg_list']
        st.session_state.bot_validated = 0

    try:
        # Check if user has access to the model in bot_info's model_config
        if st.session_state.bot_info['model_config']['model'] not in st.session_state.user['key_supported_models_list']:
            # Swap the model with the first model in the user's key_supported_models_list
            st.session_state.bot_info['model_config']['model'] = st.session_state.user['key_supported_models_list'][0]
            st.session_state.bot_info['model_overwritten'] = True 

        s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])

        new_model = None 

        if 'model_overwritten' in st.session_state.bot_info and st.session_state.bot_info['model_overwritten']:
            new_model = st.session_state.bot_info['model_config']['model']
            
        chat_session = s.create_session(
            user_id=st.session_state.user['id'], 
            bot_id=st.session_state.bot_info['id'], 
            oai_api_key=st.session_state.user['api_key'],
            overwritten_model = new_model
        )
        st.session_state.session_id = chat_session['session_info']['session_id']
        st.session_state.session_bot_id = chat_session['session_info']['session_data']['bot_id']
        # Create a session state variables to hold messages 
        st.session_state.session_msg_list = []
        bot_message = chat_session['session_response']['bot_message']
        st.session_state.session_msg_list.append({'is_user':False, 'message':bot_message})
    except s.OpenAIError as e:
        _cleanup_handler_start_session_exception()
        if e.error_type == "RateLimitError" and str(e) == "OpenAI: You exceeded your current quota, please check your plan and billing details.": 
            st.error(f"{e}  \n  \n**Friendly reminder:** If you are using a free-trial OpenAI API key, this error is caused by the extremely low rate limits associated with the key. To optimize your chat experience, we recommend upgrading to the pay-as-you-go OpenAI plan. Please see our FAQ for more information.")
        else:
            st.error(f"{e}")
    except (s.SessionNotRecorded, s.PromptNotRecorded, s.MessageNotRecorded)  as e:
        _cleanup_handler_start_session_exception()
        st.error("Could not start a session with the AI assistant. Please try again later.")
    except (s.BadRequest, Exception) as e:
        _cleanup_handler_start_session_exception()
        st.error("Something went wrong. Could not start a session with the AI assistant. Please try again later.")


def handler_user_chat():
    user_message = st.session_state.user_chat_input.replace("\n","")
    st.session_state.session_msg_list.append({"message":user_message, "is_user": True})

    s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])

    def _cleanup_handler_user_chat_exception():
        if "bot_info" in st.session_state:
            del st.session_state['bot_info']
        if "session_id" in st.session_state:
            del st.session_state['session_id']
        if "session_bot_id" in st.session_state:
            del st.session_state['session_bot_id']
        if "session_msg_list" in st.session_state:
            del st.session_state['session_msg_list']
        st.session_state.bot_validated = 0

    try:
        session_response = s.get_session_response(session_id=st.session_state.session_id, oai_api_key=st.session_state.user['api_key'], user_message=user_message)
        if session_response:
            if session_response['user_message_flagged'] == True:
                flagged_categories_str = ", ".join(session_response['user_message_flagged_categories'])
                st.warning(f"Your most recent chat message was flagged by OpenAI's content moderation endpoint for: {flagged_categories_str}")
            st.session_state.session_msg_list.append({"message":session_response['bot_message'], "is_user": False})
        st.session_state.user_chat_input= "" # clearing text box 
    except s.OpenAIError as e:
        _cleanup_handler_user_chat_exception()
        if e.error_type == "RateLimitError" and str(e) == "OpenAI: You exceeded your current quota, please check your plan and billing details.": 
            st.error(f"{e}  \n  \n**Friendly reminder:** If you are using a free-trial OpenAI API key, this error is caused by the extremely low rate limits associated with the key. To optimize your chat experience, we recommend upgrading to the pay-as-you-go OpenAI plan. Please see our FAQ for more information.")
        else:
            st.error(f"{e}")
    except (s.SessionAttributeNotUpdated, s.PromptNotRecorded, s.MessageNotRecorded)  as e:
        _cleanup_handler_user_chat_exception()
        st.error("Session or chat data could not be recorded. Please try again later.")
    except (s.BadRequest, Exception) as e: 
        _cleanup_handler_user_chat_exception()
        st.error("Unknown error. Try again later.")


def handler_session_end():
    s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])

    def _cleanup_handler_session_end_exception():
        if "bot_info" in st.session_state:
            del st.session_state['bot_info']
        if "session_id" in st.session_state:
            del st.session_state['session_id']
        if "session_bot_id" in st.session_state:
            del st.session_state['session_bot_id']
        if "session_msg_list" in st.session_state:
            del st.session_state['session_msg_list']
        st.session_state.bot_validated = 0

    try:
        session_response = s.get_session_response(session_id=st.session_state.session_id, oai_api_key=st.session_state.user['api_key'], user_message=st.session_state.bot_info['summary_prompt_msg'])
        if session_response:
            st.session_state.session_msg_list.append({"message":session_response['bot_message'], "is_user": False})
    except s.OpenAIError as e: 
        _cleanup_handler_session_end_exception()
    except (s.SessionAttributeNotUpdated, s.PromptNotRecorded, s.MessageNotRecorded) as e:
        _cleanup_handler_session_end_exception()
        st.error("Session was not wrapped up properly. Please try again later.")
    except (s.BadRequest , Exception) as e: 
        _cleanup_handler_session_end_exception()
        st.error("Unknown error. Try again later.")
    st.session_state.session_ended = 1 
    st.session_state.user_chat_input= "" # clearing text box 
    try:
        s.end_session(st.session_state['session_id'])
    except Exception as e:
        pass # purposely swallow all sort of exceptions. no point trouble users

def handler_session_rating(liked):

    s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])
    user_liked = s.UserLiked.LIKED.value 
    if liked == False:
        user_liked = s.UserLiked.DISLIKED.value
    s.rate_session(session_id=st.session_state.session_id, user_liked=user_liked)
    st.info("Thank you for rating your session!")


def handler_bot_cancellation():
    st.session_state.bot_validated = 0 
    del st.session_state.bot_info 
    url_params = st.experimental_get_query_params()
    if bool(url_params) == True and 'assistant_id' in url_params:
        st.experimental_set_query_params(assistant_id="")


def handler_load_past_session(session_id,bot_id):
    s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])
    st.session_state['session_msg_list'] = []
    session_messages = s.get_session_messages(session_id=session_id)
    for session_message in session_messages:
        if session_message['role'] == 'user':
            st.session_state.session_msg_list.append({'is_user':True,'message':session_message['message']})
        else:
            st.session_state.session_msg_list.append({'is_user':False, 'message': session_message['message']})
    st.session_state['session_id']=session_id
    st.session_state.bot_validated = 1
    st.session_state['session_bot_id']=bot_id


def handler_generate_chat_csv():
    chat_message = st.session_state.session_msg_list

    # convert the list of dictionarie
    csv_buffer = io.StringIO()
    csv_writer = csv.writer(csv_buffer)

    csv_writer.writerow(["is_user","message"])

    for message in chat_message:
        csv_writer.writerow([message['is_user'], message["message"]])
    
    return csv_buffer.getvalue()    


# centralize logic to go back to the lounge 
def handler_back_to_lounge(): 
    if "bot_info" in st.session_state:
        del st.session_state['bot_info']
    if "session_id" in st.session_state:
        del st.session_state['session_id']
    if "session_bot_id" in st.session_state:
        del st.session_state['session_bot_id']
    if "session_ended" in st.session_state:
        del st.session_state['session_ended']
    if "session_msg_list" in st.session_state:
        del st.session_state['session_msg_list']
    st.session_state.bot_validated = 0
    vutil.switch_page('lounge')



def render_user_login_required():
    st.title("AI Assistant")
    st.write("Discover other Assistants in the Lounge, or locate a specific Assistant by its personalized code.")
    #st.markdown("---")
    ac.robo_avatar_component()
    st.write("\n")
    uu = vuser.app_user()
    uu.view_get_info()


def render_bot_search():
    st.title("AI Assistant")
    st.write("Discover other Assistants in the Lounge, or locate a specific Assistant by its personalized code.")
    #st.markdown("---")
    ac.robo_avatar_component()
    st.write("\n")
    search_container = st.container()
    with search_container:
        st.text_input("Find an AI Assistant by entering its personalized code", key = "bot_search_input", on_change=handler_bot_search, args=(search_container,))
    st.write("or")
    if st.button("Back to Lounge"):
        handler_back_to_lounge()


def render_bot_details(bot):
    title_str = "{0}: AI {1}".format(bot['name'],bot['tag_line'])
    st.title(title_str)
    st.write("\n")
    avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}".format(bot['name'])
    button_label="Start chatting with {0}".format(bot['name'])
    button_key="Bot_Details_{0}".format(bot["id"])
    col1, col2 = st.columns([1, 5])
    col1.image(avatar_url, width=50)
    if st.session_state.bot_info['model_config']['model'] not in st.session_state.user['key_supported_models_list']:
        # Swap the model with the first model in the user's key_supported_models_list
        st.session_state.bot_info['model_config']['model'] = st.session_state.user['key_supported_models_list'][0]
        st.session_state.bot_info['model_overwritten'] = True 
    
    model_overwrite = col2.selectbox(
        label="GPT Model", 
        options=(
            st.session_state.user['key_supported_models_list']),
            key='assistant_model_name', 
            help="The assistant's default GPT model is currently selected. You may overwrite the model by selecting a different one.",
            index=st.session_state.user['key_supported_models_list'].index(st.session_state.bot_info['model_config']['model']),
    )

    if model_overwrite != st.session_state.bot_info['model_config']['model']:
        st.session_state.bot_info['model_config']['model'] = model_overwrite
        st.session_state.bot_info['model_overwritten'] = True 

    col2.write("Assistant Description:")
    col2.write(bot['description'])

    st.write("\n")

    col1, col2 = st.columns(2)
    col1.button("Start a new session with {0}".format(bot['name']), key = "bot_confirm", on_click=handler_start_session)
    col2.button("Find another AI assistant", key = "bot_cancel", on_click=handler_bot_cancellation)


    s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])
    past_sessions = []
    sessions = s.get_past_sessions(user_id=st.session_state['user']['id'], bot_id=st.session_state['bot_info']['id'])

    if len(sessions)>0:
        for session in sessions: 
            # ignoring anything that has less than 2 messages since those are likely abandoned errors 
            if session['message_count'] > 2:
                past_sessions.append({
                    'id':session['id'], 
                    'message_count':session['message_count'], 
                    'created_date':ag.format_datetime(session['created_date']),
                    'model': session['bot_model']
                    })               
    
    if len(past_sessions) > 0:
        st.write("\n")
        st.write("Or revisit a past session")
        col1, col2, col3, col4 = st.columns([2,2,1,4])
        col1.write("Session time")
        col2.write("GPT Model")
        col3.write("Messages")
        for past_session in past_sessions: 
            button_key="session_{0}".format(past_session["id"])
            col1, col2, col3, col4 = st.columns([2,2,1,4])
            col1.write(past_session['created_date'])
            col2.write(str(past_session['model']))            
            col3.write(str(past_session['message_count']))
            col4.button(label="Resume session", key=button_key, on_click=handler_load_past_session,args=(past_session['id'],bot['id'],))
            #st.write(past_session['id'])
    
    # st.write(st.session_state)

def render_chat_session():
    title_str = "{0}: AI {1}".format(st.session_state.bot_info['name'],st.session_state.bot_info['tag_line'])
    st.title(title_str)

    if st.session_state.session_ended == 0:

        if len(st.session_state.session_msg_list) > 5:

            with st.sidebar:
                st.write("")
                st.button(f"Conclude chat with {st.session_state.bot_info['name']}",
                key = "end_session",
                on_click=handler_session_end,
                help=f"After concluding your chat with {st.session_state.bot_info['name']}, you will be able to view a recap of your session, download a transcript of your chat, and rate your session."
                )

        # input box 
        st.text_input(
            "Talk to {0}".format(st.session_state.bot_info['name']), 
            key = "user_chat_input",
            on_change=handler_user_chat
        )
            
        st.markdown("""___""")
        # Chat module 
        for i in range(len(st.session_state.session_msg_list)-1,-1,-1): # chat in st.session_state.session_msg_list:
            render_message(st.session_state.session_msg_list[i]['is_user'], st.session_state.bot_info['name'], st.session_state.session_msg_list[i]['message'])
    
    # st.write(st.session_state)

    if st.session_state.session_ended == 1: 
        st.write("Session Recap")
        message = st.session_state.session_msg_list[-1]['message']

        st.markdown(message.replace("\n","  \n"))


        st.divider()

        with st.container():
            col1, col2, col3, col4 = st.columns([3,1,1,2]) 
            col1.write(f"Did you enjoy your session with {st.session_state.bot_info['name']}?")
            col2.button("👍", use_container_width=True, on_click=handler_session_rating, args=(True,))
            col3.button("👎", use_container_width=True, on_click=handler_session_rating, args=(False,))


        st.write("")
        csv_data = handler_generate_chat_csv()
        col1, col2, col3 = st.columns(3)

        col1.download_button("Download chat session", data=csv_data, file_name="chat_session.csv", mime="text/csv")

        if col2.button("Return to lounge"):
            handler_back_to_lounge
        



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

if "session_bot_id" in st.session_state and "bot_info" in st.session_state: 
    # mix match between session bot ID and bot id 
    # caused by user navigating to the Lounge before ending a session and choosing a different bot from the lounge 
    if st.session_state.session_bot_id != st.session_state['bot_info']['id']: 
        if "session_msg_list" in st.session_state:
            del st.session_state['session_msg_list']
        del st.session_state['session_bot_id']
        del st.session_state['session_id']

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

with st.sidebar:
    ac.st_button(url="https://twitter.com/dclin", label="Let's connect", font_awesome_icon="fa-twitter")
    ac.st_button(url="https://www.buymeacoffee.com/gptlab", label="Buy me a coffee", font_awesome_icon="fa-coffee")
    ac.st_button(url="https://gptlab.beehiiv.com/subscribe", label="Subscribe to news and updates", font_awesome_icon="fa-newspaper-o")


st.write(st.session_state)
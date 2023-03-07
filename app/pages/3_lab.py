import streamlit as st 
import api_bots as ab 
import api_sessions as asessions 

import app_user as uv 
import app_component as au
import app_utils as vutil

st.set_page_config(
    page_title="GPT Lab - Lab",
    page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"#,
    #menu_items={"About": "GPT Lab is a user-friendly app that allows anyone to interact with and create their own AI Assistants powered by OpenAI's GPT-3 language model. Our goal is to make AI accessible and easy to use for everyone, so you can focus on designing your Assistant without worrying about the underlying infrastructure.", "Get help": None, "Report a Bug": None}
)


st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)


factory_intro="Create your own custom AI assistant in three easy steps. Access it later in the Lounge or share it with friends and family. Unleash endless possibilities with your own AI assistant!"

help_msg_coaching="Designed to provide guidance and support, the Coaching personality generates responses that are informative, motivational, and helpful."
help_msg_creative="Ideal for chatbots that aim to inspire and encourage creativity, the Creative personality generates imaginative and thought-provoking responses."
help_msg_truthful="Ideal for chatbots that are designed to provide accurate information and support, the Truthful and Helpful personality generates informative and trustworthy responses."
help_msg_sarcastic="This personality generates responses with a sarcastic tone, designed to bring a touch of humor and irony to conversations."
help_msg_witty="Designed to generate lighthearted, humorous responses, this personality is perfect for chatbots that aim to entertain and bring a smile to the user's face."
help_msg_personality="Personalize your AI's responses by selecting from pre-defined personalities, each with unique settings for model temperature, frequency penalty, presence penalty, and top P. Or create your own custom personality to perfectly suit your needs."

help_msg_model="""
A model in AI refers to a specific version of an AI language processing system. The five models offered in the dropdown are:  \n
* gpt-3.5-turbo: Same model as the one powering ChatGPT. Great for advanced language processing tasks and generating human-like text. \n
* text-davinci-003: This is the most advanced model, capable of handling a wide range of tasks including natural language understanding and generation, question answering, summarization, and translation.  \n
* text-curie-001: This model is optimized for answering questions and providing information, making it ideal for chatbots and virtual assistants.  \n
* text-babbage-001: This model is designed for coding assistance, providing help with syntax and code completion.  \n
* text-ada-001: This model is optimized for text generation tasks such as summarization, translation, and text completion.
"""

help_msg_max_token = "OpenAI sets a limit on the number of tokens, or individual units of text, that each language model can generate in a single response. For example, text-davinci-003 has a limit of 4000 tokens, while other models have a limit of 2000 tokens. It's important to note that this limit is inclusive of the length of the initial prompt and all messages in the chat session. To ensure the best results, adjust the max token per response based on your specific use case and anticipated dialogue count and length in a session."
#help_msg_session_type = "The type of conversation the AI will support. In Question and Answer, the user asks the AI a question and receives a single response. Brainstorming and coaching are back-and-forth conversations with the AI. In brainstorming sessions, the AI retains a rolling conversation, meaning that only the most recent exchanges are displayed and older exchanges are gradually forgotten. In coaching sessions, the AI retains the context of the conversation."
help_msg_session_type = "The type of back-and-forth conversation the AI will support. In brainstorming sessions, the AI retains a rolling conversation, meaning that only the most recent exchanges are displayed and older exchanges are gradually forgotten. In coaching sessions, the AI retains the context of the conversation."
help_msg_initial_prompt = "The initial prompt is the most crucial part of the AI configuration, as it sets the context for the conversation and guides the AI's responses. It is the hidden set of instructions for the AI. The initial prompt should clearly convey the topic or task that you would like the AI to focus on during the conversation."
help_msg_summary_prompt = "Prompt to help the AI summarize the session"
help_msg_description = "Description shows up in the lounge"
help_msg_tag_line = "Tag line shows in chat sessions"
help_msg_model_temperature = "Controls how creativity in AI's response"
help_msg_model_top_p = "Prevents AI from giving certain answers that are too obvious"
help_msg_model_freq_penalty = "Encourages AI to be more diverse in its answers"
help_msg_model_presence_penalty = "Prevents AI from repeating itself too much"

model_params = {
    'Coaching': {
        'temperature': 0.5,
        'frequency_penalty': 0.3,
        'presence_penalty': 0.2,
        'top_p': 0.9,
        'helper_text':help_msg_coaching
    },
    'Creative': {
        'temperature': 1.0,
        'frequency_penalty': 0.1,
        'presence_penalty': 0.1,
        'top_p': 0.7,
        'helper_text':help_msg_creative
    },
    'Sarcastic': {
        'temperature': 0.8,
        'frequency_penalty': 0.1,
        'presence_penalty': 0.1,
        'top_p': 0.9,
        'helper_text':help_msg_sarcastic
    },
    'Truthful': {
        'temperature': 0.5,
        'frequency_penalty': 0.1,
        'presence_penalty': 0.2,
        'top_p': 0.9,
        'helper_text':help_msg_truthful
    },
    'Witty': {
        'temperature': 0.7,
        'frequency_penalty': 0.1,
        'presence_penalty': 0.1,
        'top_p': 0.9,
        'helper_text':help_msg_witty
    },
    'Custom': {
        'temperature': 0.7,
        'frequency_penalty': 0.0,
        'presence_penalty': 0.0,
        'top_p': 1.0,
        'helper_text': 'Customize your own AI personality'
    }
}

model_personality_list = list(model_params.keys())

ai_models_list = ['gpt-3.5-turbo', 'text-davinci-003', 'text-curie-001', 'text-babbage-001', 'text-ada-001']


b = ab.bots()
session_types = []
for session_type in b.SessionType:
    friendly_name = session_type.name.title().replace("_", " ")
    session_types.append((friendly_name, session_type))


def render_lab_step_one():
    st.title("Lab")
    st.markdown(factory_intro)
    #st.markdown("---")
    au.robo_avatar_component()
    #st.write("\n")
    st.markdown("---")
    st.markdown("### Step 1: Initial Prompt and AI Personality")

    st.markdown("##### Initial Prompt")   
    st.write(help_msg_initial_prompt)

    restart_disabled=True
    advance_disabled=True
    max_token_limit=2500 
   
    if 'lab_bot' not in st.session_state:
        st.text_area(label="Initial Prompt", key="lab_bot_initial_prompt", max_chars=2000, height=250,disabled=button_enabled)
    else:
        st.text_area(label="Initial Prompt", key="lab_bot_initial_prompt", value=st.session_state.lab_bot['initial_prompt_msg'], max_chars=2000, height=250,disabled=button_enabled)
    st.write("\n")
    st.markdown("##### AI Personality")
    st.markdown("Fine-tuning the GPT-3 model to give your AI its unique personality.")

    if 'lab_bot' in st.session_state:
        restart_disabled=False

    col1, col2 = st.columns(2)

    if 'lab_model_index' not in st.session_state:
        col1.selectbox(label="Model", options=(ai_models_list),key='lab_model_name', help=help_msg_model, disabled=button_enabled)
    else:
        col1.selectbox(label="Model", options=(ai_models_list),key='lab_model_name', help=help_msg_model, disabled=button_enabled, index=st.session_state.lab_model_index)

    st.session_state.lab_model_index = ai_models_list.index(st.session_state.lab_model_name)

    if st.session_state.lab_model_index != 0:
        max_token_limit = 1250

    if 'lab_bot' not in st.session_state:
        col2.number_input(label="AI Response Token Limit", key='lab_model_max_tokens', min_value=0, max_value=max_token_limit, value=250, step=50, help=help_msg_max_token, disabled=button_enabled)
    else:
        col2.number_input(label="AI Response Token Limit", key='lab_model_max_tokens', min_value=0, max_value=max_token_limit, value=st.session_state.lab_model_max_tokens_input, step=50, help=help_msg_max_token, disabled=button_enabled)
    st.session_state.lab_model_max_tokens_input = st.session_state.lab_model_max_tokens

    st.markdown("\n")

    if 'lab_bot' not in st.session_state:
        personality = st.selectbox(label="Personality Template", key='lab_personality', options=(model_personality_list), help=help_msg_personality, disabled=button_enabled)
    else:
        personality = st.selectbox(label="Personality Template", key='lab_personality', options=(model_personality_list), help=help_msg_personality, disabled=button_enabled, index=st.session_state.lab_model_personality_index)
    st.session_state.lab_model_personality_index = model_personality_list.index(st.session_state.lab_personality)

    st.write(model_params[personality]['helper_text'])

    expand_model_params = False

    if personality == "Custom":
        expand_model_params = True 

    if st.session_state.lab_bot_initial_prompt != "":
        advance_disabled = False 


    model_param_expander = st.expander("Advanced Model Parameters", expanded=expand_model_params)

    with model_param_expander:
        col1, col2 = st.columns(2)
        if 'lab_bot' not in st.session_state:
            if personality != "Custom":
                col1.slider(label="Temperature", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['temperature'], key='lab_model_temperature', help=help_msg_model_temperature, disabled=True)
                col1.slider(label="Top P", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['top_p'], key='lab_model_top_p', help=help_msg_model_top_p, disabled=True)
                col2.slider(label="Frequency penalty", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['frequency_penalty'], key='lab_model_frequency_penalty', help=help_msg_model_freq_penalty, disabled=True)
                col2.slider(label="Presence penalty", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['presence_penalty'], key='lab_model_presence_penalty', help=help_msg_model_presence_penalty, disabled=True)   
            else:
                col1.slider(label="Temperature", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['temperature'], key='lab_model_temperature', help=help_msg_model_temperature, disabled=False)
                col1.slider(label="Top P", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['top_p'], key='lab_model_top_p', help=help_msg_model_top_p, disabled=False)
                col2.slider(label="Frequency penalty", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['frequency_penalty'], key='lab_model_frequency_penalty', help=help_msg_model_freq_penalty, disabled=False)
                col2.slider(label="Presence penalty", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['presence_penalty'], key='lab_model_presence_penalty', help=help_msg_model_presence_penalty, disabled=False)   
        else:
            if personality != "Custom": 
                col1.slider(label="Temperature", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['temperature'], key='lab_model_temperature', help=help_msg_model_temperature, disabled=True)
                col1.slider(label="Top P", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['top_p'], key='lab_model_top_p', help=help_msg_model_top_p, disabled=True)
                col2.slider(label="Frequency penalty", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['frequency_penalty'], key='lab_model_frequency_penalty', help=help_msg_model_freq_penalty, disabled=True)
                col2.slider(label="Presence penalty", min_value=0.0, max_value=1.0, step=0.1, value=model_params[personality]['presence_penalty'], key='lab_model_presence_penalty', help=help_msg_model_presence_penalty, disabled=True)   
            else:
                col1.slider(label="Temperature", min_value=0.0, max_value=1.0, step=0.1, value=st.session_state['lab_bot']['model_config']['temperature'], key='lab_model_temperature', help=help_msg_model_temperature, disabled=False)
                col1.slider(label="Top P", min_value=0.0, max_value=1.0, step=0.1, value=st.session_state['lab_bot']['model_config']['top_p'], key='lab_model_top_p', help=help_msg_model_top_p, disabled=False)
                col2.slider(label="Frequency penalty", min_value=0.0, max_value=1.0, step=0.1, value=st.session_state['lab_bot']['model_config']['frequency_penalty'], key='lab_model_frequency_penalty', help=help_msg_model_freq_penalty, disabled=False)
                col2.slider(label="Presence penalty", min_value=0.0, max_value=1.0, step=0.1, value=st.session_state['lab_bot']['model_config']['presence_penalty'], key='lab_model_presence_penalty', help=help_msg_model_presence_penalty, disabled=False)   


    st.write("\n")
    st.write("\n")
    st.write("\n")


    col1, col2, col3 = st.columns(3)
    col1.button("Start over", disabled=restart_disabled, on_click=handle_lab_restart)
    col2.button("Skip the test drive", disabled=advance_disabled, on_click=handler_lab_step_two_confirm)
    col3.button("Test drive your AI", disabled=advance_disabled, on_click=handler_lab_step_one_confirm, type="primary")


def render_lab_step_two():
    st.title("Lab")
    st.markdown(factory_intro)
    #st.markdown("---")
    au.robo_avatar_component()
    st.write("\n")

    # input box 
    st.markdown("### Step 2: Test Chat with AI")

    col1, col2 = st.columns(2)
    col1.button("Back to Step 1", disabled=button_enabled, on_click=handler_lab_step_one_return)
    col2.button("Looks Good. Proceed to Step 3", disabled=button_enabled, on_click=handler_lab_step_two_confirm)

    st.text_input(                
        "Talk to AI", 
        key = "lab_user_chat_input",
        on_change=handler_user_chat,
        disabled=button_enabled
    )
        
    st.markdown("""___""")
    # Chat module 
    for i in range(len(st.session_state.lab_msg_list)-1,-1,-1): # chat in st.session_state.session_msg_list:
        render_message(st.session_state.lab_msg_list[i]['is_user'], st.session_state.lab_msg_list[i]['message'])    


def render_message(is_user, message):
    avatar_url = "https://api.dicebear.com/5.x/avataaars-neutral/svg?seed=ARoN&radius=25&backgroundColor=f8d25c"

    if is_user == False:
        avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb&radius=25" 

    col1, col2 = st.columns([1, 5], gap="small")
    #col1, col2, col3 = st.columns([1, 5, 1], gap="small")
    col1.image(avatar_url, width=50)
    col2.markdown(message.replace("\n","  \n"))
    # if is_user == True:
    #     col3.image(avatar_url, width=50)
    # else:
    #     col1.image(avatar_url, width=50)
    st.write("\n")


def render_lab_step_three():
    st.title("Lab")
    st.markdown(factory_intro)
    #st.markdown("---")
    au.robo_avatar_component()
    st.markdown("---")
    st.write("\n")

    # input box 
    st.markdown("### Step 3: Finalize AI")

    st.markdown("##### Name your AI")

    col1, col2 = st.columns(2)
    col1.text_input(label="Name", key="lab_bot_name", max_chars=30)
    col2.text_input(label="Tag Line", key="lab_bot_tagline", help=help_msg_tag_line, max_chars=25)
    st.text_area(label="Description", key="lab_bot_description", help=help_msg_description, max_chars=250)

    bot_avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}&radius=25".format('gptLAb') 
    bot_name = '[Name]'
    bot_tagline = '[Tag Line]'
    bot_description = '[Description]'

    if 'lab_bot_name' in st.session_state and st.session_state.lab_bot_name != "": 
        bot_avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}&radius=25".format(st.session_state.lab_bot_name) 
        bot_name = st.session_state.lab_bot_name

    if 'lab_bot_tagline' in st.session_state and st.session_state.lab_bot_tagline != "":
        bot_tagline = st.session_state.lab_bot_tagline

    if 'lab_bot_description' in st.session_state and st.session_state.lab_bot_description != "":
        bot_description = st.session_state.lab_bot_description        

    st.write("\n")
    st.markdown("##### Previews")
    col1, col2 = st.columns(2)
    col1.markdown("**Lounge preview**")
    with col1:
        col1a, col1b = st.columns([1,5])
        col1a.image(bot_avatar_url, width=50)
        col1b.markdown(f"{bot_name} - {bot_tagline}")
    button_label="Chat with {0}".format(bot_name)
    button_key = "Factory_Bot_Preview"
    col1.write("{0}".format(bot_description))
    col1.button(button_label, key=button_key, disabled=True)
    col2.markdown("**Chat session title preview**")
    title_str = "{0}: AI {1}".format(bot_name, bot_tagline)
    col2.title(title_str)
    st.write("\n")

    st.markdown("##### Summary prompt and session type")

    st.text_area(label="Summary Prompt", key="lab_prompt_summary", help=help_msg_summary_prompt, max_chars=500)
    st.selectbox(label="Session Type", key='lab_bot_session_type', help=help_msg_session_type, options = [t[0] for t in session_types], index=0)

    st.markdown("\n")
    st.markdown("\n")
    st.markdown("\n")

    col1, col2 = st.columns(2)
    col1.button("Back to Step 1", key='lab_bot_cancel', on_click=handler_lab_step_one_return)
    col2.button("Looks good. Create {0}!".format(bot_name), key='lab_bot_creation_confirm', on_click=handler_lab_step_three_confirm)



def handle_lab_restart():
    if "lab_bot" in st.session_state:
        del st.session_state['lab_bot']
    if "lab_msg_list" in st.session_state:
        del st.session_state['lab_msg_list']
    if 'lab_bot_id' in st.session_state:
        del st.session_state.lab_bot_id 
    if "lab_model_index" in st.session_state:
        del st.session_state.lab_model_index
    if "lab_model_personality_index" in st.session_state:
        del st.session_state.lab_model_personality_index
    if "lab_model_max_tokens_input" in st.session_state:
        del st.session_state.lab_model_max_tokens_input

    st.session_state.lab_active_step = 1


def handler_lab_step_one_confirm():
    if st.session_state.lab_bot_initial_prompt != "":
        st.session_state.lab_active_step = 2
        st.session_state.lab_bot = {
            'session_type': 'BRAIN_STORMING',
            'initial_prompt_msg': st.session_state.lab_bot_initial_prompt,
            'summary_prompt_msg': 'Recap what we have discussed today',
            'model_config': {
                'model': st.session_state.lab_model_name,
                'max_tokens': st.session_state.lab_model_max_tokens,
                'temperature': st.session_state.lab_model_temperature,
                'top_p': st.session_state.lab_model_top_p,
                'frequency_penalty': st.session_state.lab_model_frequency_penalty,
                'presence_penalty': st.session_state.lab_model_presence_penalty
            }
        }

        try:
            s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])
            chat_session = s.create_session(user_id=st.session_state.user['id'], bot_config_dict=st.session_state.lab_bot, oai_api_key=st.session_state.user['api_key'])
            st.session_state.lab_session_id = chat_session['session_info']['session_id']
            # Create a session state variables to hold messages 
            st.session_state.lab_msg_list = []
            bot_message = chat_session['session_response']['bot_message']
            st.session_state.lab_msg_list.append({'is_user':False, 'message':bot_message})
        except s.OpenAIClientCredentialError as e:
            del st.session_state['user']
            st.session_state.user_validated = 0 
            st.session_state.lab_active_step = 1
            st.error("OpenAI credential error. API key may be invalid, expired, revoked, or does not have right permissions.")
        except s.OpenAIConnectionError as e:
            st.session_state.lab_active_step = 1
            del st.session_state['lab_bot']
            st.error("Could not start a session with the AI assistant. OpenAI is experiencing some technical difficulties.")
        except s.OpenAIClientRateLimitError as e:
            st.session_state.lab_active_step = 1
            del st.session_state['lab_bot']
            st.error("Could not start a session with the AI assistant. Exceeded OpenAI rate limit. Please try again later.")
        except s.OpenAIClientConnectionError as e:
            st.session_state.lab_active_step = 1
            del st.session_state['lab_bot']
            st.error("Could not start a session with the AI assistant. Could not establish connection with OpenAI. Please try again later.")
        except (s.BadRequest, s.SessionNotRecorded, s.MessageNotRecorded, s.PromptNotRecorded, Exception) as e:
            st.session_state.lab_active_step = 1
            del st.session_state['lab_bot']
            st.error("Something went wrong. Could not start a session with the AI assistant. Please try again later.")

    else:
        st.warning("Missing Initial Prompt")



def handler_lab_step_one_return():
    st.session_state.lab_active_step = 1
    st.session_state.lab_msg_list=[] # clear test chat history 
    st.session_state.lab_msg_prompt = "" # clear test session prompt 

def handler_lab_step_two_confirm():
    if "lab_bot" not in st.session_state:
        if st.session_state.lab_bot_initial_prompt != "":
            st.session_state.lab_active_step = 2
            st.session_state.lab_bot = {
                'initial_prompt_msg': st.session_state.lab_bot_initial_prompt,
                'model_config': {
                    'model': st.session_state.lab_model_name,
                    'max_tokens': st.session_state.lab_model_max_tokens,
                    'temperature': st.session_state.lab_model_temperature,
                    'top_p': st.session_state.lab_model_top_p,
                    'frequency_penalty': st.session_state.lab_model_frequency_penalty,
                    'presence_penalty': st.session_state.lab_model_presence_penalty
                }
            }
        else:
            st.warning("Missing Initial Prompt")

    if "lab_bot" in st.session_state:
        st.session_state.lab_active_step = 3
        st.session_state.lab_msg_list=[] # clear test chat history 
        st.session_state.lab_msg_prompt = "" # clear test session prompt 

def handler_lab_step_three_confirm():

    selected_friendly_name = st.session_state.lab_bot_session_type
    selected_enum = next((t[1] for t in session_types if t[0] == selected_friendly_name), None)

    st.session_state['lab_bot'].update({
        'name': st.session_state.lab_bot_name,
        'tag_line': st.session_state.lab_bot_tagline,
        'session_type':selected_enum.value,
        'description': st.session_state.lab_bot_description,
        'summary_prompt_msg': st.session_state.lab_prompt_summary,
        'is_active': True  
    })

    bot_dict = st.session_state.lab_bot
    bot_id = b.create_bot(bot_config=bot_dict,user_id=st.session_state['user']['id'])
    if bot_id:
        st.balloons()
        st.session_state.lab_active_step = 4  
        st.session_state.lab_bot_id=bot_id
    else:
        st.warning("Something went wrong. Please try again.")


def handler_user_chat():
    user_message = st.session_state.lab_user_chat_input
    st.session_state.lab_msg_list.append({"message":user_message.replace("\n", "  \n"), "is_user": True})

    s = asessions.sessions(user_hash=st.session_state['user']['user_hash'])
    try:
        session_response = s.get_session_response(session_id=st.session_state.lab_session_id, oai_api_key=st.session_state.user['api_key'], user_message=user_message)
        if session_response:
            st.session_state.lab_msg_list.append({"message":session_response['bot_message'], "is_user": False})
        st.session_state.lab_user_chat_input= "" # clearing text box 
    except s.OpenAIClientCredentialError as e:
        del st.session_state['user']
        st.session_state.user_validated = 0 
        st.session_state.lab_active_step = 1
        st.error("OpenAI credential error. API key may be invalid, expired, revoked, or does not have right permissions.")
    except s.OpenAIConnectionError as e:
        st.session_state.lab_active_step = 1
        del st.session_state['lab_bot']
        st.error("Could not get AI response. OpenAI is experiencing some technical difficulties.")
    except s.OpenAIClientRateLimitError as e:
        st.session_state.lab_active_step = 1
        del st.session_state['lab_bot']
        st.error("Could not get AI response. Exceeded OpenAI rate limit. Please try again later.")
    except s.OpenAIClientConnectionError as e:
        st.session_state.lab_active_step = 1
        del st.session_state['lab_bot']
        st.error("Could not get AI response. Could not establish connection with OpenAI. Please try again later.")
    except (s.BadRequest, s.SessionNotRecorded, s.MessageNotRecorded, s.PromptNotRecorded, Exception) as e:
        st.session_state.lab_active_step = 1
        del st.session_state['lab_bot']
        st.error("Something went wrong. Could not get AI response. Please try again later.")


button_enabled = True 

if 'user_validated' in st.session_state and st.session_state.user_validated == 1:
    button_enabled = False 

if 'user' not in st.session_state or st.session_state.user_validated != 1:
    st.title("Lab")
    st.markdown(factory_intro)
    #st.markdown("---")
    au.robo_avatar_component()
    st.write("\n")
    vu = uv.app_user()
    vu.view_get_info()

if 'lab_active_step' not in st.session_state:
    st.session_state.lab_active_step = 1

# used to store test chat session messages 
if 'lab_msg_list' not in st.session_state:
    st.session_state.lab_msg_list = []

if 'lab_bot_id' not in st.session_state:
    st.session_state.lab_bot_id = None 


if st.session_state.user_validated == 1 and st.session_state.lab_active_step == 1:
    render_lab_step_one()

if st.session_state.user_validated == 1 and st.session_state.lab_active_step == 2:
    render_lab_step_two()

if st.session_state.user_validated == 1 and st.session_state.lab_active_step == 3:
    render_lab_step_three()

if st.session_state.user_validated == 1 and st.session_state.lab_active_step == 4 and st.session_state.lab_bot_id != None:
    st.title("Lab")
    st.markdown(factory_intro)
    #st.markdown("---")
    au.robo_avatar_component()
    st.write("\n")
    st.write("Congratulations on creating your own personalized AI Assistant!")
    st.info(f"Here is your personalized AI code: {st.session_state.lab_bot_id}.")
    st.write("Share this code with others to allow them to interact with your AI in the Assistnat page. Also, you can always find all your AI assistants in the Lounge.") 
    col1, col2 = st.columns(2)
    col1.button("Create another AI", on_click=handle_lab_restart())
    if col2.button("Back to Lounge"):
        handle_lab_restart()
        vutil.switch_page('lounge')

#st.write(st.session_state)
import streamlit as st 
from app import app_user as lu 
from api import api_bots as ab 
from app import app_utils as au 
from app import app_component as ac 
import random as r 

st.set_page_config(
    page_title="GPT Lab - Lounge",
    page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"#,
    #menu_items={"About": "GPT Lab is a user-friendly app that allows anyone to interact with and create their own AI Assistants powered by OpenAI's GPT-3 language model. Our goal is to make AI accessible and easy to use for everyone, so you can focus on designing your Assistant without worrying about the underlying infrastructure.", "Get help": None, "Report a Bug": None}
)


st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)

      
def view_bot_grid(bot_dict, button_disabled=False, show_bot_id=False): 

    col1, col2 = st.columns(2)

    for i in range(0,len(bot_dict)):
        avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}".format(bot_dict[i]['name'])
        button_label="Chat with {0}".format(bot_dict[i]['name'])
        button_key="Lounge_bot_{0}".format(bot_dict[i]["id"])
        if i%2 == 0:
            col1.image(avatar_url, width=50)
            col1.write(bot_dict[i]['description'])
            if show_bot_id == True:
                col1.write("Assistant ID: {0}".format(bot_dict[i]['id']))
            if col1.button(button_label, key=button_key, disabled=button_disabled):
                st.session_state.bot_info=bot_dict[i]
                st.session_state.bot_validated = 1           
                au.switch_page('assistant')
            col1.write("\n\n")
        else:
            col2.image(avatar_url, width=50)
            col2.write(bot_dict[i]['description'])
            if show_bot_id == True:
                col2.write("Assistant ID: {0}".format(bot_dict[i]['id']))
            if col2.button(button_label, key=button_key, disabled=button_disabled):
                st.session_state.bot_info=bot_dict[i]
                st.session_state.bot_validated = 1           
                au.switch_page('assistant')
            col2.write("\n\n")


#user_bots

b = ab.bots()
sb = b.get_bots(is_show_cased=True)


st.title("Lounge")
st.write("Hang out with AI assistants")
#st.markdown("---")
ac.robo_avatar_component()
st.markdown("  \n")

if 'user_validated' not in st.session_state or st.session_state.user_validated != 1:
    st.write("\n")
    uu = lu.app_user()
    uu.view_get_info()

    st.write("Come chat with our pre-trained AI assistants.")
    view_bot_grid(bot_dict=sb, button_disabled=True)


if 'user_validated' in st.session_state and st.session_state.user_validated == 1:
    button_enabled = False 
    mb = b.get_bots(user_id=st.session_state.user['id'])
    showcased_bots, my_bots  = st.tabs(['Showcased', 'My AI Assistants'])
    with showcased_bots:
        st.markdown("\n")
        st.markdown("##### Meet our showcased AI assistants!  ")
        view_bot_grid(bot_dict=sb, button_disabled=button_enabled)
    with my_bots:
        if len(mb) > 0:
            st.markdown("\n")
            st.markdown("##### Chat with your AI assistants!")
            view_bot_grid(bot_dict=mb, button_disabled=button_enabled, show_bot_id=True)
        else:
            st.markdown("\n")
            col1, col2, col3 = st.columns([1, 4, 2])
            col1.image("https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}".format(r.randint(0,168)*r.randint(0,888)), width=50)
            col2.write("You have not created your own AI assistants yet.")
            clicked = col2.button("Visit the Lab")
            if clicked:
                au.switch_page('lab')

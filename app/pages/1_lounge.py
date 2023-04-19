import streamlit as st 
import app_user as lu 
import api_bots as ab 
import app_utils as au 
import app_component as ac 
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

with st.sidebar:
    ac.st_button(url="https://twitter.com/dclin", label="Let's connect", font_awesome_icon="fa-twitter")
    ac.st_button(url="https://www.buymeacoffee.com/gptlab", label="Buy me a coffee", font_awesome_icon="fa-coffee")
    ac.st_button(url="https://gptlab.beehiiv.com/subscribe", label="Subscribe to news and updates", font_awesome_icon="fa-newspaper-o")

      
def view_bot_grid(bot_dict, button_disabled=False, show_bot_id=False): 

    col1, col2 = st.columns(2)

    for i in range(0,len(bot_dict)):
        avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}".format(bot_dict[i]['name'])
        button_label="Chat with {0}".format(bot_dict[i]['name'])
        button_key="Lounge_bot_{0}".format(bot_dict[i]["id"])
        if i%2 == 0:
            with col1:
                cola, colb = st.columns([1,5])
                cola.image(avatar_url, width=50)
                if show_bot_id == False:
                    colb.markdown(f"{bot_dict[i]['name']} - {bot_dict[i]['tag_line']}")
                else:
                    colb.markdown(f"{bot_dict[i]['name']} - {bot_dict[i]['tag_line']}  \nAssistant ID: {bot_dict[i]['id']}")
            col1.write(bot_dict[i]['description'])
            if 'user'in st.session_state and st.session_state.user['id'] is not None:
                col1.write(f"Session{'s' if bot_dict[i]['sessions_started'] > 1 else ''}: {bot_dict[i]['sessions_started']}")
            if col1.button(button_label, key=button_key, disabled=button_disabled):
                st.session_state.bot_info=bot_dict[i]
                au.switch_page('assistant')
            col1.write("\n\n")
        else:
            with col2:
                col2a, col2b = st.columns([1,5])
                col2a.image(avatar_url, width=50)
                if show_bot_id == False:
                    col2b.markdown(f"{bot_dict[i]['name']} - {bot_dict[i]['tag_line']}")
                else:
                    col2b.markdown(f"{bot_dict[i]['name']} - {bot_dict[i]['tag_line']}  \nAssistant ID: {bot_dict[i]['id']}")
            col2.write(bot_dict[i]['description'])
            if 'user'in st.session_state and st.session_state.user['id'] is not None:
                col2.write(f"Session{'s' if bot_dict[i]['sessions_started'] > 1 else ''}: {bot_dict[i]['sessions_started']}")
            if col2.button(button_label, key=button_key, disabled=button_disabled):
                st.session_state.bot_info=bot_dict[i]
                au.switch_page('assistant')
            col2.write("\n\n")


#user_bots

b = ab.bots()
sb = b.get_bots(is_show_cased=True)
r.shuffle(sb)


st.title("Lounge")
st.write("Explore our Lounge and hang out with featured AI Assistants. Chat with showcased or your own assistants.")
#st.markdown("---")
ac.robo_avatar_component()
st.markdown("  \n")

if 'user' not in st.session_state or st.session_state.user['id'] is None:
    st.write("\n")
    uu = lu.app_user()
    uu.view_get_info()

    st.write("Come chat with our pre-trained AI assistants.")
    view_bot_grid(bot_dict=sb, button_disabled=True)
else:
    button_enabled = False 
    mb = b.get_bots(user_id=st.session_state.user['id'])
    showcased_bots, my_bots  = st.tabs(['Showcased', 'My AI Assistants'])
    with showcased_bots:
        st.markdown("\n")
        st.markdown("##### Meet our showcased AI assistants!  ")
        view_bot_grid(bot_dict=sb, button_disabled=button_enabled)
    with my_bots:
        if len(mb) > 0:
            r.shuffle(mb)
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


# st.write(st.session_state)
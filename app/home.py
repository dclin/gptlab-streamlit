import streamlit as st 

st.set_page_config(
    page_title="GPT Lab",
    page_icon="https://api.dicebear.com/5.x/bottts-neutral/svg?seed=gptLAb"#,
    #menu_items={"About": "GPT Lab is a user-friendly app that allows anyone to interact with and create their own AI Assistants powered by OpenAI's GPT-3 language model. Our goal is to make AI accessible and easy to use for everyone, so you can focus on designing your Assistant without worrying about the underlying infrastructure.", "Get help": None, "Report a Bug": None}
)


import app_user as uv 
import app_component as au
#import random as r 



# copies 
home_title = "GPT Lab"
home_introduction = "Welcome to GPT Lab, where the power of OpenAI's GPT-3 technology is at your fingertips. Socialize with pre-trained AI assistants in the Lounge or create your own custom AI companions in the Lab. Personal helper, writing partner, life coach - whatever you need, GPT Lab has you covered!"
home_privacy = "GPT Lab is designed with your privacy in mind. Our system only identifies you by the hashed value of your OpenAI API Key, rather than any other personal identifiable information. This ensures your complete privacy and anonymity in our system. Our app uses your OpenAI API key to access AI functionality only during the duration of each visit, which is why you need to enter the same key every time you visit."

st.markdown(
    "<style>#MainMenu{visibility:hidden;}</style>",
    unsafe_allow_html=True
)

#st.title(home_title)
st.markdown(f"""# {home_title} <span style=color:#2E9BF5><font size=5>Beta</font></span>""",unsafe_allow_html=True)

st.markdown("""\n""")
st.markdown("""\n""")
st.markdown("#### Greetings")
st.write(home_introduction)

#st.markdown("---")
au.robo_avatar_component()

st.markdown("#### Privacy")
st.write(home_privacy)

st.markdown("""\n""")
st.markdown("""\n""")

st.markdown("#### Get Started")

vu = uv.app_user()
if 'user' not in st.session_state or st.session_state.user_validated != 1:
    vu.view_get_info()
else:
    vu.view_success_confirmation()

st.markdown("\n")
st.markdown("\n")

col1, col2 = st.columns(2)
with col1:
    au.st_button(url="https://gptlab.beehiiv.com/subscribe", label="Subscribe to news and updates", font_awesome_icon="fa-newspaper-o")

with col2:
    au.st_button(url="https://www.buymeacoffee.com/gptlab", label="Buy me a coffee", font_awesome_icon="fa-coffee")

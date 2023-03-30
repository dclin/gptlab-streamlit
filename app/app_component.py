import streamlit as st
import streamlit.components.v1 as c 
import random as r 



#@st.cache(show_spinner=False, suppress_st_warning=True,ttl=600)
def buy_me_coffee_component():
    c.html("""
    <div style="position: fixed; bottom: 5px; right: 5px;">
    <a href="https://www.buymeacoffee.com/gptlab" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/arial-yellow.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
    </div>
    """, height=70)

#@st.cache(show_spinner=False, suppress_st_warning=True,ttl=600)
def robo_avatar_component():

    robo_html = "<div style='display: flex; flex-wrap: wrap; justify-content: left;'>"
    robo_avatar_seed = [0, 'aRoN', 'gptLAb', 180, 'nORa', 'dAVe', 'Julia', 'WEldO', 60]

    for i in range(1, 10):
        avatar_url = "https://api.dicebear.com/5.x/bottts-neutral/svg?seed={0}".format(robo_avatar_seed[i-1])#format((i)*r.randint(0,888))
        robo_html += "<img src='{0}' style='width: {1}px; height: {1}px; margin: 10px;'>".format(avatar_url, 50)
    robo_html += "</div>"

    robo_html = """<style>
          @media (max-width: 800px) {
            img {
              max-width: calc((100% - 60px) / 6);
              height: auto;
              margin: 0 10px 10px 0;
            }
          }
        </style>""" + robo_html
    
    c.html(robo_html, height=70)

#@st.cache(show_spinner=False, suppress_st_warning=True,ttl=600)
def email_subscription_component():
  subscription_html = """
  <iframe src="https://embeds.beehiiv.com/f6b878de-073b-4ba2-a900-1f42e5fcfc0b?slim=true" 
          data-test-id="beehiiv-embed" 
          frameborder="0" 
          scrolling="no" 
          style="margin: 0; 
          border-radius: 5px !important; 
          background-color: transparent;">
  </iframe>"""
  c.html(subscription_html, height=80)


def st_button(url, label, font_awesome_icon):
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">', unsafe_allow_html=True)
    button_code = f'''<a href="{url}" target=_blank><i class="fa {font_awesome_icon}"></i>   {label}</a>'''
    return st.markdown(button_code, unsafe_allow_html=True)

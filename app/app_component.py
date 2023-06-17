import streamlit as st
import streamlit.components.v1 as c 
import random as r 


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


def st_button(url, label, font_awesome_icon):
    st.markdown('<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">', unsafe_allow_html=True)
    button_code = f'''<a href="{url}" target=_blank><i class="fa {font_awesome_icon}"></i>   {label}</a>'''
    return st.markdown(button_code, unsafe_allow_html=True)


def render_cta():
  with st.sidebar:
      st.write("Let's connect!")
      st_button(url="https://twitter.com/dclin", label="Twitter", font_awesome_icon="fa-twitter")
      st_button(url="http://linkedin.com/in/d2clin/", label="LinkedIn", font_awesome_icon="fa-linkedin")

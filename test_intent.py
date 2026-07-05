import streamlit as st
from dotenv import load_dotenv

# Ensure page configuration is set first
st.set_page_config(page_title="ChatWise AI Tutor", page_icon="🎓", layout="wide")

from auth import render_auth_page, render_profile_page
from chat import render_chat_page

def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "username" not in st.session_state:
        st.session_state.username = None
    if "page" not in st.session_state:
        st.session_state.page = "auth"
    if "current_chat_id" not in st.session_state:
        st.session_state.current_chat_id = None

def main():
    load_dotenv()
    init_session_state()
    
    if not st.session_state.logged_in:
        render_auth_page()
    else:
        # Enforce page routing for authenticated users
        if st.session_state.page == "profile":
            render_profile_page()
        else:
            render_chat_page()

if __name__ == "__main__":
    main()

import json
import os
import hashlib
import re
import streamlit as st
from typing import Dict, Any, Optional

USERS_FILE = "users.json"

def load_users() -> Dict[str, Any]:
    if not os.path.exists(USERS_FILE):
        return {}
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def save_users(users: Dict[str, Any]) -> None:
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

def login_user(username: str, password: str) -> bool:
    users = load_users()
    if username in users:
        if users[username]["password"] == hash_password(password):
            return True
    return False

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    if not username or not email or not password:
        return False, "All fields are required."
    
    if not is_valid_email(email):
        return False, "Invalid email format."
    
    users = load_users()
    if username in users:
        return False, "Username already exists."
    
    for u in users.values():
        if u.get("email") == email:
            return False, "Email already registered."
            
    users[username] = {
        "email": email,
        "password": hash_password(password)
    }
    save_users(users)
    return True, "Registration successful."

def update_profile(username: str, new_email: str) -> tuple[bool, str]:
    if not is_valid_email(new_email):
        return False, "Invalid email format."
        
    users = load_users()
    for u, data in users.items():
        if u != username and data.get("email") == new_email:
            return False, "Email already used by another account."
            
    if username in users:
        users[username]["email"] = new_email
        save_users(users)
        return True, "Profile updated successfully."
    return False, "User not found."

def change_password(username: str, current_pwd: str, new_pwd: str) -> tuple[bool, str]:
    users = load_users()
    if username in users and users[username]["password"] == hash_password(current_pwd):
        users[username]["password"] = hash_password(new_pwd)
        save_users(users)
        return True, "Password updated successfully."
    return False, "Incorrect current password."

def reset_password(username: str, email: str, new_pwd: str) -> tuple[bool, str]:
    users = load_users()
    if username in users:
        expected_email = users[username].get("email", "")
        if expected_email and email.lower().strip() == expected_email.lower().strip():
            users[username]["password"] = hash_password(new_pwd)
            save_users(users)
            return True, "Password reset successfully."
        else:
            return False, "Incorrect email."
    return False, "Username not found."

# ----------------- UI Components -----------------

def render_auth_page():
    st.title("Welcome to ChatWise")
    
    tab1, tab2, tab3 = st.tabs(["Login", "Register", "Forgot Password"])
    
    with tab1:
        st.subheader("Login")
        login_username = st.text_input("Username", key="log_user")
        login_password = st.text_input("Password", type="password", key="log_pass")
        if st.button("Login"):
            if login_user(login_username, login_password):
                st.session_state.logged_in = True
                st.session_state.username = login_username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
                
    with tab2:
        st.subheader("Register")
        reg_username = st.text_input("Username", key="reg_user")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_pass")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_conf")
        
        if st.button("Register"):
            if reg_password != reg_confirm:
                st.error("Passwords do not match.")
            else:
                success, msg = register_user(reg_username, reg_email, reg_password)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
                    
    with tab3:
        st.subheader("Forgot Password")
        fp_username = st.text_input("Username", key="fp_user")
        fp_email = st.text_input("Recovery Email", key="fp_ans")
        fp_new_pwd = st.text_input("New Password", type="password", key="fp_pwd")
        fp_conf_pwd = st.text_input("Confirm New Password", type="password", key="fp_conf")
        
        if st.button("Reset Password"):
            if fp_new_pwd != fp_conf_pwd:
                st.error("Passwords do not match.")
            else:
                success, msg = reset_password(fp_username, fp_email, fp_new_pwd)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)

def render_profile_page():
    st.title("User Profile")
    st.write(f"Logged in as: **{st.session_state.username}**")
    
    users = load_users()
    current_email = users.get(st.session_state.username, {}).get("email", "")
    
    with st.expander("Update Profile"):
        new_email = st.text_input("Email", value=current_email)
        if st.button("Save Profile"):
            success, msg = update_profile(st.session_state.username, new_email)
            if success:
                st.success(msg)
            else:
                st.error(msg)
                
    with st.expander("Change Password"):
        curr_pwd = st.text_input("Current Password", type="password")
        new_pwd = st.text_input("New Password", type="password", key="cp_new")
        conf_pwd = st.text_input("Confirm New Password", type="password", key="cp_conf")
        if st.button("Update Password"):
            if new_pwd != conf_pwd:
                st.error("New passwords do not match.")
            else:
                success, msg = change_password(st.session_state.username, curr_pwd, new_pwd)
                if success:
                    st.success(msg)
                else:
                    st.error(msg)
                    
    if st.button("Back to Chat"):
        st.session_state.page = "chat"
        st.rerun()
        
    if st.button("Logout", type="primary"):
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.page = "auth"
        st.rerun()

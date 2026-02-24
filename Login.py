import streamlit as st
from backend.database import register_user, login_user, init_db

init_db()

st.title("🔐 TeleQuiz Login")

tab1, tab2 = st.tabs(["Login", "Register"])

with tab1:
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        user = login_user(email, password)
        if user:
            st.session_state.user_id = user["user_id"]
            st.session_state.role = user["role"]
            st.switch_page("pages/Quiz.py")
        else:
            st.error("Invalid credentials")

with tab2:
    name = st.text_input("Name")
    email_r = st.text_input("Email", key="r1")
    pass_r = st.text_input("Password", type="password", key="r2")
    if st.button("Register"):
        register_user(name, email_r, pass_r)
        st.success("Registered successfully")
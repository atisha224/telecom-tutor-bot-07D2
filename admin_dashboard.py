import streamlit as st

st.set_page_config(page_title="Admin Dashboard", layout="wide")

st.title("Admin Monitoring Panel")

st.metric("Total Users", 128)
st.metric("Documents Indexed", 45)
st.metric("Average Score", "7.2")

st.markdown("---")

st.subheader("System Logs")
st.text_area("Logs", "No critical errors detected.", height=200)
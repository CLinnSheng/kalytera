import streamlit as st

name = st.session_state["name"]
colour = st.session_state["colour"]

st.title("Profiles")
st.write(f"Your name is {name} and favourite colour is {colour}")
submit = st.button("Go back")
if submit:
    st.switch_page("main.py")

import streamlit as st

skill = st.session_state["skill"]
current_position = st.session_state["current_position"]

st.title("Profiles")
st.write(f"Skill to learn is {skill} and current job is {current_position}")
submit = st.button("Go back")
if submit:
    st.switch_page("main.py")

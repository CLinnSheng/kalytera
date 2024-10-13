import streamlit as st
from main import main

current_position = st.session_state["current_position"]
skill = st.session_state["skill"]
new_position = st.session_state["new_position"]
response = st.session_state["response"]

st.title("Here are some advices from Kalytera!")
st.markdown(f"""
**Current job**: {current_position}

**Desired job**: {new_position}

**Existing skills**: {skill}
""")
st.markdown("**Advices**:") 
st.markdown(response)

submit = st.button("Go back")
if submit:
    st.switch_page("main.py")

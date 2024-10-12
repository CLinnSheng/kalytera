import streamlit as st

def main():
    st.title("Kalytera")

    # Create a sidebar for input
    with st.sidebar:
        with st.form("professional_profile"):
            job_title = st.text_input("Desired Job Title")
            skillset = st.text_input("Skillset (comma separated)")
            current_job_title = st.text_input("Current Job Title")
            submitted = st.form_submit_button("Submit")

    # Display result in main page
    if submitted:
            st.write("Your Professional Profile:")
            st.write(f"Desired Job Title: {job_title}")
            st.write(f"Skillset: {skillset}")
            st.write(f"Current Job Title: {current_job_title}")

if __name__ == "__main__":
    main()

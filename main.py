import streamlit as st
from ai import ai

st.set_page_config(initial_sidebar_state="collapsed", layout="wide")

if "name" not in st.session_state:
    st.session_state["name"] = ""

if "skill" not in st.session_state:
    st.session_state["skill"] = ""

if "current_position" not in st.session_state:
    st.session_state["current_position"] = ""

if "new_position" not in st.session_state:
    st.session_state["new_position"] = ""

# Custom CSS to style the left column with a background image
st.markdown(
    """
    <style>
    .stMainBlockContainer {
        background-color: rgba(0, 0, 0, 0);
        padding-bottom: 0px;
        padding-top: 0px;
        padding-left: 0px;
    }
    
    
    .left-column {
        background-image: url('https://img.freepik.com/free-photo/abstract-autumn-beauty-multi-colored-leaf-vein-pattern-generated-by-ai_188544-9871.jpg'); /* Replace this URL with your own image */
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-color: rgba(0, 0, 0, 0);
        height: 97vh; /* Full height */
        padding: 0; 
        margin: 0;
        border-radius: 10px;
    }
    
    .right-column {
        padding: 0px;
    }
    
    [data-testid="stMain"] div:first-child{
        background-color: rgba(0, 0, 0, 0);
    }
    
    [data-testid="stHeader"]{
        background-color: rgba(0, 0, 0, 0);
    }
    
    </style>
    """,
    unsafe_allow_html=True
)


def main():
    # Divide the page into two columns
    col1, col2 = st.columns([2, 1], gap="small", vertical_alignment="center")  # You can adjust the ratio [1, 1.5] to change the column sizes

    # Left column for the image (background image applied with CSS)
    with col1:
        st.markdown('<div class="left-column"></div>', unsafe_allow_html=True)

    # Right column for input fields
    with col2:
        st.title("Simple Streamlit App")

        current_position = st.text_input("What is your current position?", st.session_state["current_position"])
        new_position = st.text_input("What job do you wish to transition into?", st.session_state["new_position"])
        skill = st.text_input("What skills do you have?", st.session_state["skill"])
        
        submit = st.button("Submit")
        if submit:
            if not skill.strip() or not current_position.strip():
                st.warning("Please fill in all fields!")

            else:
                st.session_state["skill"] = skill
                st.session_state["current_position"] = current_position
                st.session_state["new_position"] = new_position
                response = ai(current_position, new_position, skill)
                st.session_state["response"] = response
                print(response)
                st.switch_page("pages/Profile.py")
            


if __name__ == "__main__":
    main()

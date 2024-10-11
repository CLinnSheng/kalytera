import streamlit as st
#
st.set_page_config(initial_sidebar_state="collapsed", layout = "wide")
#
if "name" not in st.session_state:
    st.session_state["name"] = ""

if "colour" not in st.session_state:
    st.session_state["colour"] = ""
#
# st.title("Simple Streamlit App")
#
# name = st.text_input("Enter name:", st.session_state["name"])
# colour = st.selectbox("Select your favourite colour", ["", "Red", "Green", "Blue"])
#
# submit = st.button("Submit")
# if submit:
#     st.session_state["name"] = name
#     st.session_state["colour"] = colour
#     st.switch_page("pages/Profile.py")
#     st.write(f"You have entered {name} and favourite colour is {colour}")



# Set up page layout to be wide
# st.set_page_config(layout="wide")

# Custom CSS to style the left column with a background image
st.markdown(
    """
    <style>
    .left-column {
        background-image: url('https://img.freepik.com/free-photo/abstract-autumn-beauty-multi-colored-leaf-vein-pattern-generated-by-ai_188544-9871.jpg'); /* Replace this URL with your own image */
        background-size: cover;
        background-position: center;
        height: 75vh; /* Full height */
        padding: 0px;
    }
    .right-column {
        padding: 0px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Divide the page into two columns
col1, col2 = st.columns([2, 1])  # You can adjust the ratio [1, 1.5] to change the column sizes

# Left column for the image (background image applied with CSS)
with col1:
    st.markdown('<div class="left-column"></div>', unsafe_allow_html=True)

# Right column for input fields
with col2:
    st.title("Simple Streamlit App")

    name = st.text_input("Enter name:", st.session_state["name"])
    colour = st.selectbox("Select your favourite colour", ["", "Red", "Green", "Blue"])

    submit = st.button("Submit")
    if submit:
        st.session_state["name"] = name
        st.session_state["colour"] = colour
        st.switch_page("pages/Profile.py")
        st.write(f"You have entered {name} and favourite colour is {colour}")



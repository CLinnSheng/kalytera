import streamlit as st

# Set page configuration (for fullscreen view and title)
st.set_page_config(page_title="Login", layout="wide")

# Custom CSS styling to match your image design
st.markdown("""
    <style>
    [data-testid="stAppViewContainer"]{
        background-image: url("https://img.freepik.com/free-photo/abstract-autumn-beauty-multi-colored-leaf-vein-pattern-generated-by-ai_188544-9871.jpg");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-width: 100vw;
        background-height: 100vh;
    }
    
    [data-testid="stHeader"]{
        background-color: rgba(0, 0, 0, 0);
    }
    
    .stMainBlockContainer {
        background-color: rgba(0, 0, 0, 0);
        padding-bottom: 0px;
        padding-top: 0px;
        padding-right: 150px;
        padding-left: 150px;
    }
    
    .stTextInput {
        width: 400px;
        position: center;
    }
    
    
    .login-container {
        background-color: #f0f8ff;
        padding: 50px;
        border-radius: 15px;
        width: 400px;
        margin: auto;
        margin-top: 75px;
    }
    .login-button {
        background-color: #007BFF; 
        color: white; 
        font-size: 18px; 
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
    }
    .login-button:hover {
        background-color: #0056b3;
    }
    .form-title {
        font-family: Arial, sans-serif;
        font-size: 24px;
        text-align: center;
        color: #333;
        margin-bottom: 30px;
    }
    .login-input {
        width: 100%;
        padding: 10px;
        border-radius: 5px;
        border: 1px solid #ccc;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# Create the login form layout
st.markdown('<div class="login-container">', unsafe_allow_html=True)

st.markdown('<div class="form-title">Login</div>', unsafe_allow_html=True)

email = st.text_input("Email Address", "", placeholder="youremail@gmail.com")
password = st.text_input("Password", "", type="password")

if st.button('Login'):
    if email == "youremail@gmail.com" and password == "password":  # Sample validation logic
        st.success("Welcome back!")
    else:
        st.error("Invalid login credentials.")

st.markdown('<a href="#" style="text-align: center; display: block; color: blue;">Forgot your password?</a>', unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

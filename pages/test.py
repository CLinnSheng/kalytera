import streamlit as st

page_by_img = """
<style>
[data-testid="stAppViewContainer"]{
background-image: url('https://img.freepik.com/free-photo/abstract-autumn-beauty-multi-colored-leaf-vein-pattern-generated-by-ai_188544-9871.jpg'); /* Replace this URL with your own image */
background-size: cover;
}


[data-testid="stHeader"]{
background-color: rgba(0, 0, 0, 0);
}

</style>
"""

st.markdown(page_by_img, unsafe_allow_html=True)
st.title("test")

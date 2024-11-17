import streamlit as st
from home import home_page
from comparison import comparison_page

st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Comparison"])

# Page routing
if page == "Home":
    home_page()  # Call the function from home.py
elif page == "Comparison":
    comparison_page()  # Call the function from comparison.py

import streamlit as st
from home import home_page
from comparison import comparison_page
from analysis2 import analysis_page
from an import create_pygwalker_viz

st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Comparison", "Analysis", "Customizable Data"])

# Page routing
if page == "Home":
    home_page()  # Call the function from home.py
elif page == "Comparison":
    comparison_page()  # Call the function from comparison.py
elif page == "Analysis":
    analysis_page()  # Call the function from analysis.py
elif page == "Customizable Data":
    create_pygwalker_viz()  # Call the function from analysis.py

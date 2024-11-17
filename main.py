import streamlit as st
st.set_page_config(
    page_title="US Population Dashboard",
    page_icon="🏂",
    layout="wide",
    initial_sidebar_state="collapsed",
)
from home import home_page
from comparison import comparison_page
from analysis2 import analysis_page
from an import create_pygwalker_viz
from llm_page import llm_page  # Import the new LLM page
from openai import OpenAI


# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Comparison", "Analysis", "Customizable Data", "LLM Page"]
)

# Page routing
if page == "Home":
    home_page()
elif page == "Comparison":
    comparison_page()
elif page == "Analysis":
    analysis_page()
elif page == "Customizable Data":
    create_pygwalker_viz()
elif page == "LLM Page":
    llm_page()  
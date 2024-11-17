import streamlit as st
import pandas as pd
import pygwalker as pyg

def create_pygwalker_viz():
    # Load the CSV file
    df = pd.read_csv('./updated_file.csv')

    # Create the Pygwalker visualization
    walker = pyg.walk(df, spec="./gw_config.json")

    # Display the Pygwalker visualization in Streamlit
    st.title("Make your own visualizations")

    st.markdown("""
        Allows you to explore data interactively, similar to Tableau or Power BI, directly in the web browser.
    """)

    # Render the walker as an HTML component in Streamlit
    st.components.v1.html(walker.to_html(), height=800, scrolling=True)




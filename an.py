import streamlit as st
import pandas as pd
import pygwalker as pyg
import requests
from io import StringIO

def fetch_data_from_ipfs(cid: str) -> pd.DataFrame:
    """
    Fetch a CSV file from IPFS using its CID via a public gateway.
    """
    # Use an IPFS public gateway to fetch the file
    url = f"https://gateway.pinata.cloud/ipfs/{cid}"
    response = requests.get(url)

    # Raise an error if the request was unsuccessful
    response.raise_for_status()

    # Load the CSV content into a pandas DataFrame
    data = pd.read_csv(StringIO(response.text))
    return data

def create_pygwalker_viz():
    """
    Create a Pygwalker visualization using data fetched from IPFS.
    """
    # CID of the file hosted on IPFS
    cid = "Qmaq97iYXo48jgCkHWCfYRWA7L1tfCX2JXvR71y8wnVRAh"
    
    # Fetch the data from IPFS
    df = fetch_data_from_ipfs(cid)

    # Create the Pygwalker visualization
    walker = pyg.walk(df, spec="./gw_config.json")

    # Display the Pygwalker visualization in Streamlit
    st.title("Make your own visualizations")

    st.markdown("""
        Allows you to explore data interactively, similar to Tableau or Power BI, directly in the web browser.
    """)

    # Render the walker as an HTML component in Streamlit
    st.components.v1.html(walker.to_html(), height=800, scrolling=True)

# Streamlit App
if __name__ == "__main__":
    # Call the visualization function
    create_pygwalker_viz()

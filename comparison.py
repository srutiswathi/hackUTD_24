import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from io import StringIO

def comparison_page():
    # Pinata IPFS CID and gateway URL
    ipfs_cid = "Qmaq97iYXo48jgCkHWCfYRWA7L1tfCX2JXvR71y8wnVRAh"  # Replace with your actual CID
    ipfs_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_cid}"

    # Fetch the data from IPFS
    @st.cache_data
    def fetch_data_from_ipfs(url):
        response = requests.get(url)
        if response.status_code == 200:
            csv_data = StringIO(response.text)
            return pd.read_csv(csv_data)
        else:
            st.error("Failed to fetch data from IPFS. Check the CID and URL.")
            return pd.DataFrame()  # Return empty DataFrame if fetch fails

    # Load data
    data = fetch_data_from_ipfs(ipfs_url)
    if data.empty:
        st.stop()  # Stop execution if the data could not be loaded

    st.title("Fuel Economy Comparison")
    
    # Filters
    st.write("### Filter Options")
    col1, col2 = st.columns(2)
    with col1:
        make1 = st.selectbox('Select Make 1', data['make'].unique())
        VClass1 = st.selectbox('Select Vehicle Class 1', data['assumed_VClass'].unique())
    with col2:
        make2 = st.selectbox('Select Make 2', data['make'].unique())
        VClass2 = st.selectbox('Select Vehicle Class 2', data['assumed_VClass'].unique())

    # Filter the data based on selections
    toyota_data = data[data['make'] == make1]
    kia_data = data[data['make'] == make2]

    compact_cars_toyota = toyota_data[toyota_data['VClass'] == VClass1]
    final_table_toyota_compact_cars = compact_cars_toyota.groupby('year').agg({'feScore': 'mean'})

    compact_cars_kia = kia_data[kia_data['VClass'] == VClass2]
    final_table_kia_compact_cars = compact_cars_kia.groupby('year').agg({'feScore': 'mean'})

    avg_fe_score = data[data['VClass'] == 'Compact Cars'].groupby('year').agg({'feScore': 'mean'})

    # # Display Data
    # st.write("### Data Overview")
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.write(f"**{make1} Data**")
    #     st.write(toyota_data)
    # with col2:
    #     st.write(f"**{make2} Data**")
    #     st.write(kia_data)

    # st.write("### Aggregated Data")
    # col1, col2 = st.columns(2)
    # with col1:
    #     st.write(f"**{make1} ({VClass1}) Aggregated by Year**")
    #     st.write(final_table_toyota_compact_cars)
    # with col2:
    #     st.write(f"**{make2} ({VClass2}) Aggregated by Year**")
    #     st.write(final_table_kia_compact_cars)

    # st.write("### Average Fuel Economy for Compact Cars Across All Makes")
    # st.write(avg_fe_score)

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(final_table_kia_compact_cars.index, final_table_kia_compact_cars['feScore'], marker='o', linestyle='-', label=make2)
    ax.plot(final_table_toyota_compact_cars.index, final_table_toyota_compact_cars['feScore'], marker='o', linestyle='-', label=make1)
    ax.plot(avg_fe_score.index, avg_fe_score['feScore'], color='red', linestyle='--', label='Average Fuel Economy Score')
    ax.set_title('Average Fuel Economy Score by Year for Selected Makes and Vehicle Classes')
    ax.set_xlabel('Year')
    ax.set_ylabel('Average Fuel Economy Score')
    ax.set_xticks(range(2021, 2026))
    ax.set_yticks(range(0, 11))
    ax.legend()

    # Display Plot
    st.pyplot(fig)

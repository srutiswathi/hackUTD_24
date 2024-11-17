import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import requests
from io import StringIO
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from fpdf import FPDF
import streamlit as st
import requests
import io
import os
from pinata_utils import upload_to_pinata

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

    # st.title("Fuel Economy Comparison")
    
    # # Filters
    # col = st.columns((3/5, 2/5))
    # with col[1]:
    #     st.write("Filter Options")

    col = st.columns((3, 1, 1))
    with col[0]:
        st.title("Industry-Wide Analytics")

    with col[1]:
        make1 = st.selectbox('Select Make 1', data['make'].unique())
        VClass1 = st.selectbox('Select Vehicle Class 1', data[data['make'] == make1]['assumed_VClass'].unique())
        
    with col[2]:
        make2 = st.selectbox('Select Make 2', data['make'].unique())
        VClass2 = st.selectbox('Select Vehicle Class 2', data[data['make'] == make2]['assumed_VClass'].unique())
    
    col = st.columns((2, 2))
    subcol = col[0].columns((1, 1))


    with col[0]:
        with subcol[0]:
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #393939, #1a1a1a);
                    color: white;
                    text-align: center;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                    margin-bottom: 20px;">
                    <h4>Total Cars</h4>
                    <p style='font-size: 24px; font-weight: normal;'>{make1}: {total_cars(data, make1)}</p>
                    <p style='font-size: 24px; font-weight: normal;'>{make2}: {total_cars(data, make2)}</p>

                </div>
                """,
                unsafe_allow_html=True
            )
        with subcol[1]:
            # Create the styled container for the chart and header
            st.markdown(
                f"""
                <div style="
                    background: linear-gradient(135deg, #393939, #1a1a1a, red);
                    color: white;
                    text-align: center;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                    margin-bottom: 20px;">
                    <h4>Total Cars from {make2}</h4>
                </div>
                """,
                unsafe_allow_html=True
            )
    with col[0]:
        horizontal_bar_chart(data, make1, make2, VClass1, VClass2)


            # Apply CSS to make the chart appear within the same box
            # st.markdown(
            #     """
            #     <style>
            #     .chart-container {
            #         background: linear-gradient(135deg, #393939, #1a1a1a, red);
            #         border-radius: 8px;
            #         padding: 20px;
            #         box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            #     }
            #     </style>
            #     """,
            #     unsafe_allow_html=True
            # )

            # # Create a container to house the chart
            # with st.container():
            #     st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            #     pie_chart(data, make1, make2, VClass1, VClass2)
            #     st.markdown('</div>', unsafe_allow_html=True)

    with col[0]:
        
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #393939, #1a1a1a);
                color: white;
                height: 100%;
                text-align: center;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                margin-bottom: 20px;">
                <h4>Chat With RAG</h4>
                <p style='font-size: 24px; font-weight: bold;'> {total_cars(data, make2)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col[-1]:
        fe_comparison_chart(data, make1, make2, VClass1, VClass2)

    

    




def fe_comparison_chart(data, make1, make2, VClass1, VClass2):
    # Filter the data based on selections
    toyota_data = data[data['make'] == make1]
    kia_data = data[data['make'] == make2]

    compact_cars_toyota = toyota_data[toyota_data['VClass'] == VClass1]
    final_table_toyota_compact_cars = compact_cars_toyota.groupby('year').agg({'feScore': 'mean'})

    compact_cars_kia = kia_data[kia_data['VClass'] == VClass2]
    final_table_kia_compact_cars = compact_cars_kia.groupby('year').agg({'feScore': 'mean'})

    avg_fe_score = data[data['VClass'] == 'Compact Cars'].groupby('year').agg({'feScore': 'mean'})

    # Plotting
    fig, ax = plt.subplots()

    ax.fill_between(
        avg_fe_score.index,
        avg_fe_score['feScore'],
        color='#fcf5ea',
        alpha=0.3  # Transparency for the area
    )   
    # Plot the data
    ax.plot(final_table_kia_compact_cars.index, final_table_kia_compact_cars['feScore'], marker='o', linestyle='-', label=make2, color='#ff8f88')
    ax.plot(final_table_toyota_compact_cars.index, final_table_toyota_compact_cars['feScore'], marker='o', linestyle='-', label=make1, color='#85aa7e')
    ax.plot(avg_fe_score.index, avg_fe_score['feScore'], color='#fcf5ea', linestyle='--', label='Average Fuel Economy Score')

    # Add area chart for average fuel economy without a legend entry


    # Set labels and ticks
    ax.set_xlabel('Year', color='white')
    ax.set_ylabel('Fuel Economy', color='white')
    ax.set_xticks(range(2021, 2026))
    ax.set_yticks(range(0, 11))
    ax.tick_params(axis='x', colors='white')  # Set X-axis tick color
    ax.tick_params(axis='y', colors='white')  # Set Y-axis tick color

    # Set legend (exclude the area chart from the legend)
    ax.legend(facecolor='#393939', framealpha=0.9, edgecolor='white', labelcolor='white')

    # Remove top and right spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    # Set remaining spines to white
    ax.spines['left'].set_color('white')
    ax.spines['bottom'].set_color('white')

    # Set figure background and axes background
    fig.patch.set_facecolor('#393939')
    ax.set_facecolor('#393939')

    # Set figure size
    fig.set_size_inches(10, 6)  # Set the figure size in inches (width, height)

    # Display Plot
    st.pyplot(fig)



def total_cars(data, make1):
    return( len(data[data['make'] == make1]))

# def pie_chart(data, make1, make2, VClass1, VClass2):
#     # Calculate totals
#     total1 = len(data[data['make'] == make1])
#     total2 = len(data[data['make'] == make2])
#     total = len(data)
#     total_class1 = len(data[(data['make'] == make1) & (data['assumed_VClass'] == VClass1)])
#     total_class2 = len(data[(data['make'] == make2) & (data['assumed_VClass'] == VClass2)])

#     # Data for the chart
#     labels = [
#         f"{make1} ({VClass1})",
#         f"{make2} ({VClass2})",
#         "Other Makes/Classes"
#     ]
#     sizes = [total_class1, total_class2, total - (total_class1 + total_class2)]
#     colors = ['blue', 'purple', '#D1D5DB']  # Blue for make1, Purple for make2, bg-gray-300 equivalent

#     # Create the pie chart with a hollow center
#     fig, ax = plt.subplots(figsize=(6, 6))
#     wedges, texts, autotexts = ax.pie(
#         sizes,  
#         autopct='%1.1f%%', 
#         startangle=140,
#         colors=colors,
#         pctdistance=0.85,
#         wedgeprops={'width': 0.3}  # Controls the width of the pie slices
#     )

#     # Formatting for a fully transparent background
#     plt.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle
#     fig.patch.set_alpha(0)  # Makes the figure background fully transparent
#     ax.set_facecolor("none")  # Makes the axes background fully transparent
#     for spine in ax.spines.values():  # Remove axes borders
#         spine.set_visible(False)

#     # Remove ticks for a cleaner look
#     ax.set_xticks([])
#     ax.set_yticks([])

#     # Display the pie chart in Streamlit
#     st.pyplot(fig)


import streamlit as st
import plotly.graph_objects as go

def horizontal_bar_chart(data, make1, make2, VClass1, VClass2):
    # Filter the data based on selections
    class1_size = len(data[(data['make'] == make1) & (data['assumed_VClass'] == VClass1)])
    class2_size = len(data[(data['make'] == make2) & (data['assumed_VClass'] == VClass2)])
    make1_size = len(data[data['make'] == make1]) - class1_size  # Remaining cars in make1
    make2_size = len(data[data['make'] == make2]) - class2_size  # Remaining cars in make2

    # Data for the bar chart
    labels = [make1, make2]
    class_sizes = [class1_size, class2_size]
    other_sizes = [make1_size, make2_size]

    # Create the bar chart
    fig = go.Figure()

    # Add bars for the specific class
    fig.add_trace(go.Bar(
        y=labels,
        x=class_sizes,
        orientation='h',
        name='Specific Class',
        marker=dict(color='blue'),
        hoverinfo='x+name'  # Display x value on hover
    ))

    # Add bars for other classes (stacked)
    fig.add_trace(go.Bar(
        y=labels,
        x=other_sizes,
        orientation='h',
        name='Other Classes',
        marker=dict(color='lightblue'),
        hoverinfo='x+name'
    ))

    # Layout customization
    fig.update_layout(
        barmode='stack',  # Stack bars
        plot_bgcolor='#393939',  # Dark grey background for the plot
        paper_bgcolor='#393939',  # Dark grey background for the entire figure
        xaxis=dict(
            showticklabels=False  # Hide x-axis tick labels
        ),
        yaxis=dict(
            color='white',  # Y-axis text in white
            showgrid=False  # Hide grid lines
        ),
        showlegend=False,  # Remove legend
        font=dict(color='white')  # Font color to white
    )

    fig.update_layout(
        height=190,  # Set the height of the chart
        width=800,  # Set the width of the chart
        margin=dict(l=20, r=20, t=0, b=20),
    )

    # Display Plotly chart directly in Streamlit
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


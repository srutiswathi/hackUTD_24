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
import time
import logging
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from streamlit_chat import message
import openai

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY is not set in .env or environment variables.")
openai.api_key = api_key

# Initialize OpenAI client
from openai import OpenAI
client = OpenAI(api_key=api_key)

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # You can adjust the level (INFO, WARNING, DEBUG)
logger = logging.getLogger(__name__)

# Load and preprocess the CSV file
@st.cache
def load_csv(file_path):
    df = pd.read_csv(file_path)
    df['combined_text'] = df.astype(str).apply(lambda x: ' '.join(x), axis=1)
    return df

# Generate text embeddings for the CSV data
@st.cache(allow_output_mutation=True)
def generate_embeddings(data, model_name='all-MiniLM-L6-v2'):
    model = SentenceTransformer(model_name)
    embeddings = model.encode(data['combined_text'].tolist())
    return embeddings, model

# Search for the most similar entries
def search(query, embeddings, data, model, top_n=3):
    query_embedding = model.encode([query])
    similarities = cosine_similarity(query_embedding, embeddings).flatten()
    top_indices = similarities.argsort()[-top_n:][::-1]
    results = data.iloc[top_indices]
    return results

# Query the OpenAI API using the OpenAI client (synchronously)
def query_llm(user_query, context=""):
    try:
        logger.debug("Entering query_llm function")

        # Simulate progress for LLM response generation
        with st.spinner("Generating response from the LLM..."):

            # Call OpenAI API synchronously
            logger.debug("Calling OpenAI API...")
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert vehicle chatbot."},
                    {"role": "user", "content": f"Context: {context}\n\nQuery: {user_query}"}
                ],
                max_tokens=150,
                temperature=0.1,
            )
            logger.debug(f"API Response: {response}")

            # Log the length of 'choices' in the response
            choices_length = len(response['choices']) if 'choices' in response else 0
            logger.debug(f"Number of choices in response: {choices_length}")

            return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"Error communicating with the API: {str(e)}")
        return f"Error communicating with the API: {str(e)}"

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

        # Chatbot Interface (OpenAI code added here)
        st.subheader("Chat with the Bot")
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages from the session
        for i, message_dict in enumerate(st.session_state.messages):
            message(**message_dict, key=f"message_{i}")  # Assigning a unique key

        # User input
        user_input = st.text_input("You:", key="input")
        if user_input and st.session_state.get("last_user_input") != user_input:
            # Process user input
            st.session_state.last_user_input = user_input

            st.subheader("Processing Your Query")
            query_progress = st.progress(0)
            with st.spinner("Searching dataset for relevant information..."):
                for i in range(1, 101, 25):  # Simulating query search progress
                    time.sleep(0.2)
                    query_progress.progress(i)
                results = search(user_input, embeddings, data, model)
            st.success("Relevant data retrieved!")
            context = "\n".join(results['combined_text'].tolist())

            # Generate response using GPT-3.5-Turbo (synchronously)
            bot_response = query_llm(user_input, context)

            # Add user message to session
            st.session_state.messages.append({"message": user_input, "is_user": True})

            # Add bot response to session
            st.session_state.messages.append({"message": bot_response, "is_user": False})

            # Optionally, display the bot's response in a text area
            st.text_area("Bot Response", value=bot_response, height=200)

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

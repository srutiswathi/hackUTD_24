import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from streamlit_chat import message
import openai
import os
import time
import logging
from dotenv import load_dotenv

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

# Main Streamlit App
def main():
    st.title("Conversational Chatbot for Vehicle Data with GPT-3.5-Turbo")

    # Dataset Loading Progress Bar
    st.subheader("Loading Dataset")
    file_path = 'filtered_file.csv'  # Adjust path if needed
    dataset_progress = st.progress(0)
    with st.spinner("Loading dataset..."):
        for i in range(1, 101, 25):  # Simulating dataset loading progress
            time.sleep(0.2)
            dataset_progress.progress(i)
        data = load_csv(file_path)
    st.success("Dataset loaded successfully!")
    st.dataframe(data.head(5))  # Display first 5 rows of the dataset

    # Embedding Generation Progress Bar
    st.subheader("Generating Embeddings")
    embedding_progress = st.progress(0)
    with st.spinner("Generating embeddings..."):
        for i in range(1, 101, 20):  # Simulating embedding generation progress
            time.sleep(0.2)
            embedding_progress.progress(i)
        embeddings, model = generate_embeddings(data)
    st.success("Embeddings generated successfully!")

    # Chatbot Interface
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

if __name__ == "__main__":
    main()


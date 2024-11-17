import streamlit as st
from LLM import load_csv, generate_embeddings, search, query_llm  # Import necessary functions from LLM.py

def llm_page():
    st.title("LLM-Powered Page")
    st.write("Welcome to the LLM-powered page!")

    # Example: Load dataset
    file_path = "filtered_file.csv"
    with st.spinner("Loading dataset..."):
        data = load_csv(file_path)
    st.success("Dataset loaded!")
    st.dataframe(data.head(5))  # Display the first 5 rows of the dataset

    # Example: Query user input
    query = st.text_input("Enter your query:")
    if query:
        with st.spinner("Generating response..."):
            embeddings, model = generate_embeddings(data)  # Generate embeddings
            results = search(query, embeddings, data, model)  # Perform search
        st.write("Search Results:")
        st.dataframe(results)

        # Use the query_llm function
        context = "\n".join(results['combined_text'].tolist())
        response = query_llm(query, context)
        st.write("LLM Response:")
        st.text(response)
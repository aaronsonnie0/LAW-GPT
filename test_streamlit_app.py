import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

st.title("Test Vector Store App")

# Initialize the embedding function
try:
    st.write("Testing Google Generative AI Embeddings...")
    
    embedding_function = GoogleGenerativeAIEmbeddings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/embedding-001"  # The correct model name with 'models/' prefix
    )
    
    # Test texts
    texts = [
        "This is the first document.",
        "This is the second document.",
        "This is the third document."
    ]
    
    # Create a vector store
    st.write("Creating vector store...")
    vector_store = Chroma.from_texts(
        texts=texts,
        embedding=embedding_function,
        persist_directory="./test_chroma_db"
    )
    
    st.success("Vector store created successfully!")
    
    # Test similarity search
    st.write("Testing similarity search...")
    query = st.text_input("Enter a query:", "Which document is first?")
    
    if query:
        results = vector_store.similarity_search(query)
        
        st.write(f"Search results for query: '{query}'")
        for i, doc in enumerate(results):
            st.write(f"Result {i+1}: {doc.page_content}")
    
except Exception as e:
    st.error(f"Error: {e}")

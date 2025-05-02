import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

# Load environment variables
load_dotenv()

# Test ChromaDB
try:
    print("Testing ChromaDB with Google Generative AI Embeddings...")
    
    # Initialize the embedding function
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
    print("Creating vector store...")
    vector_store = Chroma.from_texts(
        texts=texts,
        embedding=embedding_function,
        persist_directory="./test_chroma_db"
    )
    
    print("Vector store created successfully!")
    
    # Test similarity search
    print("Testing similarity search...")
    query = "Which document is first?"
    results = vector_store.similarity_search(query)
    
    print(f"Search results for query: '{query}'")
    for i, doc in enumerate(results):
        print(f"Result {i+1}: {doc.page_content}")
    
except Exception as e:
    print(f"Error testing ChromaDB: {e}")

import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load environment variables
load_dotenv()

# Test the embedding function
try:
    print("Testing Google Generative AI Embeddings...")
    print(f"API Key: {os.getenv('GOOGLE_API_KEY')[:5]}...")
    
    embedding_function = GoogleGenerativeAIEmbeddings(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        model="models/embedding-001"  # The correct model name with 'models/' prefix
    )
    
    # Test with a simple text
    text = "This is a test document."
    embedding = embedding_function.embed_query(text)
    
    print(f"Embedding successful! Vector length: {len(embedding)}")
    print(f"First few values: {embedding[:5]}")
    
except Exception as e:
    print(f"Error testing embeddings: {e}")

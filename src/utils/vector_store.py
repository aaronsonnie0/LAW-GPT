import os
import sys
from typing import List, Dict, Any
from dotenv import load_dotenv

# Try to import required packages
CHROMA_AVAILABLE = False
LANGCHAIN_COMMUNITY_AVAILABLE = False
EMBEDDINGS_AVAILABLE = False

try:
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    print("Warning: langchain_google_genai not available. Please install with: pip install langchain-google-genai")

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    print("Warning: chromadb not available. Please install with: pip install chromadb")

try:
    from langchain_community.vectorstores import Chroma
    LANGCHAIN_COMMUNITY_AVAILABLE = True
except ImportError:
    print("Warning: langchain_community.vectorstores.Chroma not available. Please install with: pip install langchain-community")

# Load environment variables
load_dotenv()

class VectorStore:
    """
    Utility for creating and managing vector embeddings
    """

    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the vector store

        Args:
            persist_directory: Directory to persist the vector store
        """
        self.persist_directory = persist_directory
        self.vector_store = None
        self.embedding_function = None

        # Check if all required packages are available
        if not CHROMA_AVAILABLE or not LANGCHAIN_COMMUNITY_AVAILABLE:
            print("Vector store functionality is disabled because required packages are not available.")
            print("Please install the required packages with:")
            print("pip install langchain-community chromadb")
            return

        # Check if Google API key is available
        if not os.getenv("GOOGLE_API_KEY"):
            print("Vector store functionality is disabled because Google API key is not available.")
            print("Please set the GOOGLE_API_KEY environment variable in your .env file.")
            return

        # Check if embeddings are available
        if not EMBEDDINGS_AVAILABLE:
            print("Vector store functionality is disabled because GoogleGenerativeAIEmbeddings is not available.")
            print("Please install langchain-google-genai with:")
            print("pip install langchain-google-genai")
            return

        # Initialize the embedding function
        try:
            self.embedding_function = GoogleGenerativeAIEmbeddings(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                model="models/embedding-001"  # The correct model name with 'models/' prefix
            )
        except Exception as e:
            print(f"Error initializing embedding function: {e}")
            self.embedding_function = None

    def create_from_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None):
        """
        Create a vector store from a list of texts

        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries for each text chunk
        """
        # Check if all required components are available
        if not CHROMA_AVAILABLE:
            print("Cannot create vector store: chromadb is not available")
            print("Please install with: pip install chromadb")
            return None

        if not LANGCHAIN_COMMUNITY_AVAILABLE:
            print("Cannot create vector store: langchain_community is not available")
            print("Please install with: pip install langchain-community")
            return None

        if not EMBEDDINGS_AVAILABLE:
            print("Cannot create vector store: GoogleGenerativeAIEmbeddings is not available")
            print("Please install with: pip install langchain-google-genai")
            return None

        if self.embedding_function is None:
            print("Cannot create vector store: embedding function is not initialized")
            print("Please check your Google API key in the .env file")
            return None

        try:
            self.vector_store = Chroma.from_texts(
                texts=texts,
                embedding=self.embedding_function,
                metadatas=metadatas,
                persist_directory=self.persist_directory
            )

            return self.vector_store
        except Exception as e:
            print(f"Error creating vector store: {e}")
            return None

    def create_from_clauses(self, clauses: List[Dict[str, Any]]):
        """
        Create a vector store from a list of clause dictionaries

        Args:
            clauses: List of clause dictionaries with 'id', 'text', 'type', etc.
        """
        # Check if all required components are available
        if not all([CHROMA_AVAILABLE, LANGCHAIN_COMMUNITY_AVAILABLE, EMBEDDINGS_AVAILABLE]):
            print("Cannot create vector store from clauses: Required packages are not available")
            print("Please install with: pip install langchain-community chromadb langchain-google-genai")
            return None

        if self.embedding_function is None:
            print("Cannot create vector store from clauses: Embedding function is not initialized")
            print("Please check your Google API key in the .env file")
            return None

        try:
            texts = [clause["text"] for clause in clauses]

            # Ensure metadata values are not None
            metadatas = []
            for clause in clauses:
                metadata = {
                    "id": str(clause.get("id", "")) if clause.get("id") is not None else "",
                    "type": str(clause.get("type", "")) if clause.get("type") is not None else ""
                }
                metadatas.append(metadata)

            return self.create_from_texts(texts, metadatas)
        except Exception as e:
            print(f"Error creating vector store from clauses: {e}")
            return None

    def get_retriever(self, search_kwargs=None):
        """
        Get a retriever from the vector store

        Args:
            search_kwargs: Search arguments for the retriever

        Returns:
            A retriever object or None if vector store is not available
        """
        # Check if all required components are available
        if not CHROMA_AVAILABLE:
            print("Cannot get retriever: chromadb is not available")
            print("Please install with: pip install chromadb")
            return None

        if not LANGCHAIN_COMMUNITY_AVAILABLE:
            print("Cannot get retriever: langchain_community is not available")
            print("Please install with: pip install langchain-community")
            return None

        if self.vector_store is None:
            print("Cannot get retriever: Vector store is not initialized")
            print("Please create a vector store first with create_from_texts() or create_from_clauses()")
            return None

        try:
            if search_kwargs is None:
                search_kwargs = {"k": 3}

            return self.vector_store.as_retriever(search_kwargs=search_kwargs)
        except Exception as e:
            print(f"Error getting retriever: {e}")
            return None

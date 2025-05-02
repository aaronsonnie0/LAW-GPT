import os
from typing import List, Dict, Any
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# Try to import Chroma
try:
    from langchain_community.vectorstores import Chroma
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
    print("Warning: langchain_community.vectorstores.Chroma not available. Vector store functionality will be limited.")

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

        # Check if Chroma is available
        if not CHROMA_AVAILABLE:
            print("Vector store functionality is disabled because Chroma is not available.")
            print("Please install langchain-community and chromadb with:")
            print("py -m pip install langchain-community chromadb")
            self.vector_store = None
            self.embedding_function = None
            return

        # Initialize the embedding function
        try:
            self.embedding_function = GoogleGenerativeAIEmbeddings(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                model="embedding-001"  # This is the correct model name without 'models/' prefix
            )

            # Initialize the vector store
            self.vector_store = None
        except Exception as e:
            print(f"Error initializing embedding function: {e}")
            self.embedding_function = None
            self.vector_store = None

    def create_from_texts(self, texts: List[str], metadatas: List[Dict[str, Any]] = None):
        """
        Create a vector store from a list of texts

        Args:
            texts: List of text chunks
            metadatas: List of metadata dictionaries for each text chunk
        """
        if not CHROMA_AVAILABLE or self.embedding_function is None:
            print("Cannot create vector store: Chroma or embedding function not available")
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
        if not CHROMA_AVAILABLE or self.embedding_function is None:
            print("Cannot create vector store from clauses: Chroma or embedding function not available")
            return None

        try:
            texts = [clause["text"] for clause in clauses]
            metadatas = [{"id": clause.get("id", ""), "type": clause.get("type", "")} for clause in clauses]

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
        if not CHROMA_AVAILABLE or self.vector_store is None:
            print("Cannot get retriever: Vector store not available")
            return None

        try:
            if search_kwargs is None:
                search_kwargs = {"k": 3}

            return self.vector_store.as_retriever(search_kwargs=search_kwargs)
        except Exception as e:
            print(f"Error getting retriever: {e}")
            return None

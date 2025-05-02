from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class QAChain:
    """
    Question answering chain using LangChain
    """

    def __init__(self, retriever, temperature=0.0):
        """
        Initialize the QA chain

        Args:
            retriever: The retriever to use for retrieving relevant documents
            temperature: Temperature for the LLM
        """
        # Initialize the LLM
        self.llm = ChatGoogleGenerativeAI(
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            model="gemini-1.5-pro",
            temperature=temperature
        )

        # Create a custom prompt template for legal document analysis
        template = """
        You are a legal AI assistant specialized in analyzing legal documents.

        Use the following pieces of context to answer the question at the end.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        Always explain your reasoning and cite the specific clauses you're referencing.

        Context:
        {context}

        Question: {question}

        Answer:
        """

        prompt = PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )

        # Create the QA chain
        self.chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )

    def run(self, query):
        """
        Run the QA chain on a query

        Args:
            query: The query to run

        Returns:
            The response from the QA chain
        """
        try:
            # Add a timeout mechanism to prevent getting stuck
            import threading

            result_container = [None]
            error_container = [None]

            def qa_with_timeout():
                try:
                    result_container[0] = self.chain({"query": query})
                except Exception as e:
                    error_container[0] = str(e)

            # Start QA in a separate thread
            thread = threading.Thread(target=qa_with_timeout)
            thread.start()

            # Wait for the thread to complete with a timeout
            timeout = 15  # seconds
            thread.join(timeout)

            # Check if QA completed or timed out
            if thread.is_alive():
                print("QA is taking longer than expected. Using simple response.")
                return self._generate_simple_response(query)
            elif error_container[0]:
                print(f"Error during QA: {error_container[0]}. Using simple response.")
                return self._generate_simple_response(query)

            return result_container[0]
        except Exception as e:
            print(f"Error running QA chain: {e}")
            return self._generate_simple_response(query)

    def _generate_simple_response(self, query):
        """
        Generate a simple response when the QA chain fails

        Args:
            query: The user's query

        Returns:
            A simple response dictionary
        """
        return {
            "result": "I'm sorry, I couldn't process your question with the AI model. " +
                     "This could be due to missing dependencies or API limitations. " +
                     "Please try a simpler question or ensure all dependencies are properly installed.",
            "source_documents": []
        }

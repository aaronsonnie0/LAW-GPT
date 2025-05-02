import streamlit as st
import os
import tempfile
import sys
import pandas as pd
from pathlib import Path

# Add the src directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.document_parser import DocumentParser
from src.utils.text_chunker import TextChunker
from src.utils.vector_store import VectorStore
from src.utils.qa_chain import QAChain
from src.utils.ner_classifier import NERClassifier
from src.utils.document_summarizer import DocumentSummarizer
from src.utils.export_utils import ExportUtils
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Check if Google API key is set
if not os.getenv("GOOGLE_API_KEY"):
    st.warning("Google API key not found. Please set it in the .env file.")

st.set_page_config(
    page_title="LAWGPT - Legal Document Analysis",
    page_icon="⚖️",
    layout="wide"
)

st.title("⚖️ LAWGPT - Legal Document Analysis")
st.markdown("""
Upload legal documents like contracts, agreements, NDAs, etc. Then ask questions about them.
""")

# Initialize session state
if "extracted_text" not in st.session_state:
    st.session_state.extracted_text = None
if "document_name" not in st.session_state:
    st.session_state.document_name = None
if "clauses" not in st.session_state:
    st.session_state.clauses = None
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "processed_clauses" not in st.session_state:
    st.session_state.processed_clauses = None
if "document_summary" not in st.session_state:
    st.session_state.document_summary = None
if "risk_analyzed_clauses" not in st.session_state:
    st.session_state.risk_analyzed_clauses = None
if "pdf_report_path" not in st.session_state:
    st.session_state.pdf_report_path = None

# File uploader
uploaded_file = st.file_uploader("Upload a legal document", type=["pdf", "docx"])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Parse the document
        with st.spinner("Extracting text from document..."):
            extracted_text = DocumentParser.parse_document(tmp_file_path)

        if extracted_text:
            st.success("Document processed successfully!")

            # Display the extracted text in an expandable section
            with st.expander("View Extracted Text"):
                st.text_area("Document Content", extracted_text, height=400)

            # Save the extracted text in session state for later use
            st.session_state.extracted_text = extracted_text
            st.session_state.document_name = uploaded_file.name

            # Process the document into clauses
            with st.spinner("Processing document into clauses..."):
                try:
                    # Add a timeout mechanism to prevent getting stuck
                    import threading
                    import time

                    result = [None]
                    error = [None]

                    def process_with_timeout():
                        try:
                            result[0] = TextChunker.chunk_by_clauses(extracted_text)
                        except Exception as e:
                            error[0] = str(e)

                    # Start processing in a separate thread
                    thread = threading.Thread(target=process_with_timeout)
                    thread.start()

                    # Wait for the thread to complete with a timeout
                    timeout = 10  # seconds
                    thread.join(timeout)

                    # Check if processing completed or timed out
                    if thread.is_alive():
                        st.warning(f"Processing is taking longer than expected. Using simplified chunking method.")
                        # Force fallback to simple chunking
                        clauses = TextChunker._fallback_chunking(extracted_text)
                    elif error[0]:
                        st.warning(f"Error during clause processing: {error[0]}. Using simplified chunking method.")
                        clauses = TextChunker._fallback_chunking(extracted_text)
                    else:
                        clauses = result[0]

                    st.session_state.clauses = clauses
                except Exception as e:
                    st.warning(f"Error during document processing: {e}. Using simplified chunking method.")
                    # Fallback to simple chunking
                    clauses = TextChunker._fallback_chunking(extracted_text)
                    st.session_state.clauses = clauses

            # Display the clauses
            with st.expander("View Document Clauses"):
                for i, clause in enumerate(clauses):
                    st.markdown(f"**Clause {clause['id']}**")
                    st.text(clause['text'])
                    st.markdown("---")

            # Create vector embeddings
            if os.getenv("GOOGLE_API_KEY"):
                with st.spinner("Creating vector embeddings..."):
                    vector_store = VectorStore()
                    result = vector_store.create_from_clauses(clauses)
                    if result is not None:
                        st.session_state.vector_store = vector_store
                        st.success("Vector embeddings created successfully!")
                    else:
                        st.warning("Failed to create vector embeddings. Some features may not work.")
                        st.session_state.vector_store = None
                        st.error("Vector store is not available. Please check if required packages are installed.")
                        st.info("Run the following command in your terminal or command prompt:")
                        st.code("pip install langchain-community chromadb langchain-google-genai")
                        st.warning("You can still analyze clauses and generate document summaries, but question answering requires vector store functionality.")
            else:
                st.warning("Skipping vector embeddings creation. Google API key not found.")
                st.error("Please set your Google API key in the .env file to enable vector embeddings.")
                st.info("Create a .env file in the project root with the following content:")
                st.code("GOOGLE_API_KEY=your_api_key_here")
        else:
            st.error("Failed to extract text from the document.")

    except Exception as e:
        st.error(f"Error processing document: {e}")

    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)

# If we have extracted text, create tabs for different functionalities
if st.session_state.extracted_text is not None:
    tab1, tab2, tab3 = st.tabs(["Ask Questions", "Analyze Clauses", "Document Summary"])

    # Tab 1: Question Answering
    with tab1:
        st.markdown("## Ask Questions About Your Document")

        user_question = st.text_input("Enter your question about the document:")

        if user_question:
            if st.session_state.vector_store is not None:
                with st.spinner("Analyzing your question..."):
                    # Create QA chain
                    retriever = st.session_state.vector_store.get_retriever()
                    if retriever is not None:
                        qa_chain = QAChain(retriever)

                        # Run the query
                        try:
                            result = qa_chain.run(user_question)

                            # Display the answer
                            st.markdown("### Answer")
                            st.markdown(result["result"])

                            # Display the source clauses
                            st.markdown("### Source Clauses")
                            for i, doc in enumerate(result["source_documents"]):
                                st.markdown(f"**Source {i+1}**")
                                st.text(doc.page_content)
                                st.markdown(f"*Metadata: {doc.metadata}*")
                                st.markdown("---")
                        except Exception as e:
                            st.error(f"Error processing your question: {e}")
                    else:
                        st.error("Vector retriever is not available. Please check if required packages are installed.")
                        st.info("Run the following command in your terminal or command prompt:")
                        st.code("pip install langchain-community chromadb langchain-google-genai")
                        st.warning("After installing, restart the application.")
            else:
                st.error("Vector store is not available. Please check if required packages are installed.")
                st.info("Run the following command in your terminal or command prompt:")
                st.code("pip install langchain-community chromadb langchain-google-genai")
                st.warning("After installing, restart the application.")
                st.info("You can still analyze clauses and generate document summaries, but question answering requires vector store functionality.")

    # Tab 2: Clause Analysis
    with tab2:
        st.markdown("## Analyze Document Clauses")

        if st.session_state.clauses:
            # Button to process clauses with NER and classification
            if st.button("Analyze Clauses") or st.session_state.processed_clauses is not None:
                if st.session_state.processed_clauses is None:
                    with st.spinner("Analyzing clauses with NER and classification..."):
                        # Create NER classifier
                        ner_classifier = NERClassifier()

                        # Process clauses
                        processed_clauses = ner_classifier.process_clauses(st.session_state.clauses)
                        st.session_state.processed_clauses = processed_clauses

                # Display the processed clauses
                if st.session_state.processed_clauses:
                    # Create a dataframe for the clauses
                    import pandas as pd

                    clause_data = []
                    for clause in st.session_state.processed_clauses:
                        clause_data.append({
                            "ID": clause.get("id", ""),
                            "Type": clause.get("type", ""),
                            "Risk Score": clause.get("risk_score", 0),
                            "Explanation": clause.get("explanation", "")
                        })

                    df = pd.DataFrame(clause_data)

                    # Display the dataframe
                    st.dataframe(df)

                    # Display detailed clause information
                    st.markdown("### Clause Details")

                    # Add a selectbox to select a clause
                    clause_ids = [clause["id"] for clause in st.session_state.processed_clauses]
                    selected_clause_id = st.selectbox("Select a clause to view details:", clause_ids)

                    # Display the selected clause
                    selected_clause = next((clause for clause in st.session_state.processed_clauses if clause["id"] == selected_clause_id), None)

                    if selected_clause:
                        st.markdown(f"**Clause {selected_clause['id']}**")
                        st.markdown(f"**Type:** {selected_clause.get('type', 'Unknown')}")
                        st.markdown(f"**Risk Score:** {selected_clause.get('risk_score', 0)}/5")
                        st.markdown(f"**Explanation:** {selected_clause.get('explanation', '')}")

                        st.markdown("**Text:**")
                        st.text(selected_clause["text"])

                        st.markdown("**Entities:**")
                        entities = selected_clause.get("entities", {})
                        for entity_type, entity_values in entities.items():
                            st.markdown(f"*{entity_type}:* {', '.join(entity_values)}")
            else:
                st.info("Click 'Analyze Clauses' to process the document with NER and classification.")

    # Tab 3: Document Summary
    with tab3:
        st.markdown("## Document Summary")

        if st.session_state.processed_clauses:
            # Button to generate document summary
            if st.button("Generate Document Summary") or st.session_state.document_summary is not None:
                if st.session_state.document_summary is None:
                    with st.spinner("Generating document summary..."):
                        # Create document summarizer
                        document_summarizer = DocumentSummarizer()

                        # Generate document summary
                        summary = document_summarizer.summarize_document(st.session_state.processed_clauses)
                        st.session_state.document_summary = summary

                        # Analyze risks in clauses
                        risk_analyzed_clauses = document_summarizer.analyze_document_risks(st.session_state.processed_clauses)
                        st.session_state.risk_analyzed_clauses = risk_analyzed_clauses

                # Display the document summary
                if st.session_state.document_summary:
                    st.markdown(st.session_state.document_summary)

                # Display high-risk clauses
                if st.session_state.risk_analyzed_clauses:
                    st.markdown("## High-Risk Clauses")

                    # Filter clauses with high risk
                    high_risk_clauses = []
                    for clause in st.session_state.risk_analyzed_clauses:
                        risk_analysis = clause.get('risk_analysis', '')
                        if 'Risk Level: High' in risk_analysis:
                            high_risk_clauses.append(clause)

                    if high_risk_clauses:
                        for clause in high_risk_clauses:
                            with st.expander(f"Clause {clause['id']} - {clause.get('type', 'Unknown')}"):
                                st.text(clause['text'])
                                st.markdown("**Risk Analysis:**")
                                st.markdown(clause['risk_analysis'])
                    else:
                        st.info("No high-risk clauses found.")

                    # Export options
                    st.markdown("## Export Options")

                    # Export to CSV
                    if st.button("Export Clauses to CSV"):
                        # Create a dataframe for the clauses
                        clause_data = []
                        for clause in st.session_state.risk_analyzed_clauses:
                            clause_data.append({
                                "ID": clause.get("id", ""),
                                "Type": clause.get("type", ""),
                                "Risk Score": clause.get("risk_score", 0),
                                "Text": clause.get("text", "")[:100] + "..." if len(clause.get("text", "")) > 100 else clause.get("text", "")
                            })

                        df = pd.DataFrame(clause_data)

                        # Generate download link
                        csv_link = ExportUtils.get_csv_download_link(df, f"{st.session_state.document_name}_clauses.csv")
                        st.markdown(csv_link, unsafe_allow_html=True)

                    # Export to PDF
                    if st.button("Generate PDF Report") or st.session_state.pdf_report_path is not None:
                        if st.session_state.pdf_report_path is None:
                            with st.spinner("Generating PDF report..."):
                                # Create PDF report
                                pdf_path = ExportUtils.create_pdf_report(
                                    st.session_state.document_name,
                                    st.session_state.document_summary,
                                    st.session_state.processed_clauses,
                                    high_risk_clauses
                                )
                                st.session_state.pdf_report_path = pdf_path

                        if st.session_state.pdf_report_path is not None:
                            # Generate download link
                            pdf_link = ExportUtils.get_pdf_download_link(
                                st.session_state.pdf_report_path,
                                f"{st.session_state.document_name}_report.pdf"
                            )
                            st.markdown(pdf_link, unsafe_allow_html=True)
                        else:
                            st.error("PDF generation failed. Please install FPDF with: pip install fpdf")
            else:
                st.info("Click 'Generate Document Summary' to analyze the document and generate a summary.")
        elif st.session_state.clauses:
            st.warning("Please analyze clauses in the 'Analyze Clauses' tab first.")
        else:
            st.warning("Please upload a document first.")

import streamlit as st
import os
import tempfile
from pathlib import Path
import re

# Set page config
st.set_page_config(
    page_title="Simple Document Parser",
    page_icon="📄",
    layout="wide"
)

st.title("📄 Simple Document Parser")
st.markdown("""
Upload a document (PDF or DOCX) to extract and view its content.
""")

# Try to import optional dependencies
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    st.warning("PyMuPDF not available. PDF parsing with PyMuPDF will be disabled.")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    st.warning("pdfplumber not available. PDF parsing with pdfplumber will be disabled.")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    st.warning("python-docx not available. DOCX parsing will be disabled.")

def parse_pdf_pymupdf(file_path):
    """Parse PDF using PyMuPDF"""
    if not PYMUPDF_AVAILABLE:
        st.warning("PyMuPDF is not installed. Please install it with: pip install PyMuPDF")
        return None

    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text
    except Exception as e:
        st.error(f"Error parsing PDF with PyMuPDF: {e}")
        return None

def parse_pdf_pdfplumber(file_path):
    """Parse PDF using pdfplumber"""
    if not PDFPLUMBER_AVAILABLE:
        st.warning("pdfplumber is not installed. Please install it with: pip install pdfplumber")
        return None

    try:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        st.error(f"Error parsing PDF with pdfplumber: {e}")
        return None

def parse_docx(file_path):
    """Parse DOCX files"""
    if not DOCX_AVAILABLE:
        st.warning("python-docx is not installed. Please install it with: pip install python-docx")
        return None

    try:
        doc = docx.Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    except Exception as e:
        st.error(f"Error parsing DOCX: {e}")
        return None

def parse_document(file_path):
    """Parse document based on file extension"""
    _, file_extension = os.path.splitext(file_path)

    if file_extension.lower() == '.pdf':
        # Try PyMuPDF first, fall back to pdfplumber
        text = parse_pdf_pymupdf(file_path)
        if not text:
            text = parse_pdf_pdfplumber(file_path)
        return text

    elif file_extension.lower() == '.docx':
        return parse_docx(file_path)

    else:
        st.error(f"Unsupported file format: {file_extension}")
        return None

def chunk_text(text, chunk_size=1000):
    """Simple text chunking by paragraphs or fixed size"""
    if not text:
        return []
        
    # Try to split by paragraphs first
    paragraphs = text.split('\n\n')
    
    # If we have very few paragraphs, try to split by newlines
    if len(paragraphs) < 3:
        paragraphs = text.split('\n')
        
    # If we still have very few chunks, use character-based chunking
    if len(paragraphs) < 3:
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            if chunk:
                chunks.append(chunk)
        return chunks
    
    # Filter out empty paragraphs
    return [p for p in paragraphs if p.strip()]

# File uploader
uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx"])

if uploaded_file is not None:
    # Create a temporary file to save the uploaded file
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        tmp_file_path = tmp_file.name

    try:
        # Parse the document
        with st.spinner("Extracting text from document..."):
            extracted_text = parse_document(tmp_file_path)

        if extracted_text:
            st.success("Document processed successfully!")

            # Display the extracted text in an expandable section
            with st.expander("View Extracted Text", expanded=True):
                st.text_area("Document Content", extracted_text, height=300)

            # Process the document into chunks
            with st.spinner("Processing document into chunks..."):
                chunks = chunk_text(extracted_text)

            # Display the chunks
            st.subheader(f"Document Chunks ({len(chunks)})")
            for i, chunk in enumerate(chunks):
                with st.expander(f"Chunk {i+1}"):
                    st.text(chunk)
        else:
            st.error("Failed to extract text from the document.")

    except Exception as e:
        st.error(f"Error processing document: {e}")

    finally:
        # Clean up the temporary file
        os.unlink(tmp_file_path)

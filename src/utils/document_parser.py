import os

# Try to import optional dependencies
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    print("PyMuPDF not available. PDF parsing with PyMuPDF will be disabled.")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("pdfplumber not available. PDF parsing with pdfplumber will be disabled.")

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("python-docx not available. DOCX parsing will be disabled.")

class DocumentParser:
    """
    Utility class for parsing different document formats (PDF, DOCX)
    """

    @staticmethod
    def parse_pdf_pymupdf(file_path):
        """
        Parse PDF using PyMuPDF
        """
        if not PYMUPDF_AVAILABLE:
            print("PyMuPDF is not installed. Please install it with: pip install PyMuPDF")
            return None

        try:
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            print(f"Error parsing PDF with PyMuPDF: {e}")
            return None

    @staticmethod
    def parse_pdf_pdfplumber(file_path):
        """
        Parse PDF using pdfplumber (alternative method)
        """
        if not PDFPLUMBER_AVAILABLE:
            print("pdfplumber is not installed. Please install it with: pip install pdfplumber")
            return None

        try:
            text = ""
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() or ""
            return text
        except Exception as e:
            print(f"Error parsing PDF with pdfplumber: {e}")
            return None

    @staticmethod
    def parse_docx(file_path):
        """
        Parse DOCX files
        """
        if not DOCX_AVAILABLE:
            print("python-docx is not installed. Please install it with: pip install python-docx")
            return None

        try:
            doc = docx.Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except Exception as e:
            print(f"Error parsing DOCX: {e}")
            return None

    @staticmethod
    def parse_document(file_path):
        """
        Parse document based on file extension
        """
        _, file_extension = os.path.splitext(file_path)

        if file_extension.lower() == '.pdf':
            # Try PyMuPDF first, fall back to pdfplumber
            text = DocumentParser.parse_pdf_pymupdf(file_path)
            if not text:
                text = DocumentParser.parse_pdf_pdfplumber(file_path)
            return text

        elif file_extension.lower() == '.docx':
            return DocumentParser.parse_docx(file_path)

        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

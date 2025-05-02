# LAWGPT - Legal Document Analysis

LAWGPT is an enterprise-grade AI application that combines LLMs, Retrieval, Named Entity Recognition (NER), and a user-friendly interface to analyze legal documents.

## Features

- **Document Upload**: Upload legal documents in PDF or DOCX format
- **Text Extraction**: Extract text from documents using PyMuPDF and pdfplumber
- **Clause Identification**: Automatically identify and extract clauses from legal documents
- **Question Answering**: Ask questions about the document and get accurate answers with source references
- **Named Entity Recognition**: Extract entities like organizations, dates, and monetary values
- **Clause Classification**: Classify clauses by type (IP, Tax, Financial, etc.)
- **Risk Analysis**: Identify high-risk clauses and provide risk assessments
- **Document Summarization**: Generate comprehensive summaries of legal documents
- **Export Options**: Export analysis results to CSV or PDF

## Tech Stack

- **Frontend**: Streamlit
- **LLM**: Gemini Pro via Google Generative AI API
- **RAG Engine**: LangChain + ChromaDB
- **NER & Classifier**: spaCy + Gemini prompts
- **PDF Parsing**: PyMuPDF / pdfplumber
- **Document Processing**: LangChain for chunking and processing

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/lawgpt.git
cd lawgpt
```

2. Install the required packages:
```
pip install -r requirements.txt
```

3. Download the spaCy model:
```
python -m spacy download en_core_web_trf
```

4. Create a `.env` file with your API keys:
```
GOOGLE_API_KEY=your_google_api_key_here
```

## Usage

1. Run the Streamlit app:
```
python main.py
```

2. Open your browser and go to `http://localhost:8501`

3. Upload a legal document (PDF or DOCX)

4. Use the different tabs to:
   - Ask questions about the document
   - Analyze clauses and entities
   - View document summary and risk analysis
   - Export results

## Project Structure

```
lawgpt/
├── main.py                  # Main entry point
├── requirements.txt         # Project dependencies
├── .env.example             # Example environment variables
├── README.md                # Project documentation
├── src/                     # Source code
│   ├── app/                 # Streamlit application
│   │   └── app.py           # Main Streamlit app
│   ├── utils/               # Utility modules
│   │   ├── document_parser.py    # Document parsing utilities
│   │   ├── text_chunker.py       # Text chunking utilities
│   │   ├── vector_store.py       # Vector store for embeddings
│   │   ├── qa_chain.py           # Question answering chain
│   │   ├── ner_classifier.py     # NER and clause classification
│   │   ├── document_summarizer.py # Document summarization
│   │   └── export_utils.py       # Export utilities
│   ├── models/              # Model-related code
│   └── data/                # Data storage
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- OpenAI for GPT-4 API
- LangChain for the RAG framework
- Streamlit for the web interface
- spaCy for NER capabilities

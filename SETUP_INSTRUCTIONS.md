# Setup Instructions for LAWGPT

## Prerequisites

Before running LAWGPT, make sure you have the following installed:

1. **Python 3.8+**: Download and install from [python.org](https://www.python.org/downloads/)
2. **Git**: Download and install from [git-scm.com](https://git-scm.com/downloads)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/lawgpt.git
cd lawgpt
```

### 2. Create a Virtual Environment

#### Windows
```bash
python -m venv venv
venv\Scripts\activate
```

#### macOS/Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy Model

```bash
python -m spacy download en_core_web_trf
```

### 5. Set Up Environment Variables

Create a `.env` file in the root directory with your API keys:

```
GOOGLE_API_KEY=AIzaSyBcr3Uire2ma92maQnACBPMsfuaU1MrSYg
```

## Running the Application

### Option 1: Using the Run Script (Recommended)

#### Windows
Simply double-click the `run_lawgpt.bat` file or run it from the command prompt:
```
run_lawgpt.bat
```

#### macOS/Linux
Make the script executable and run it:
```bash
chmod +x run_lawgpt.sh
./run_lawgpt.sh
```

### Option 2: Manual Start

If you prefer to start the application manually:

```bash
# Windows
py -m streamlit run src/app/app.py

# macOS/Linux
python3 -m streamlit run src/app/app.py
```

The application should now be running at `http://localhost:8501`

## Troubleshooting

### Python Not Found

If you see an error like "Python was not found", make sure Python is installed and added to your PATH environment variable.

### Package Installation Issues

If you encounter issues installing packages, try:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Google API Key Issues

If you see authentication errors, check that your Google API key is correctly set in the `.env` file.

## Additional Resources

- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Google Generative AI Documentation](https://ai.google.dev/docs)

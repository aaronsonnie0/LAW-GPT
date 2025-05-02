import sys
import os

print("Python version:", sys.version)
print("Python executable:", sys.executable)
print("Current working directory:", os.getcwd())
print("Files in current directory:", os.listdir("."))

# Try importing some of our dependencies
try:
    import streamlit
    print("Streamlit version:", streamlit.__version__)
except ImportError:
    print("Streamlit is not installed")

try:
    import langchain
    print("LangChain version:", langchain.__version__)
except ImportError:
    print("LangChain is not installed")

try:
    import openai
    print("OpenAI version:", openai.__version__)
except ImportError:
    print("OpenAI is not installed")

print("\nTo install dependencies, run:")
print(f"{sys.executable} -m pip install -r requirements.txt")

print("\nTo run the app, use:")
print(f"{sys.executable} -m streamlit run src/app/app.py")

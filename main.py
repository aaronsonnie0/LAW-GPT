import streamlit as st
import subprocess
import sys

if __name__ == "__main__":
    # Run the Streamlit app
    subprocess.run([sys.executable, "-m", "streamlit", "run", "src/app/app.py"])

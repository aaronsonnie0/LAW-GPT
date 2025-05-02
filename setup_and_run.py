import os
import subprocess

def install_packages():
    """Install required packages."""
    print("Installing required packages...")

    # Upgrade pip
    subprocess.run(["py", "-m", "pip", "install", "--upgrade", "pip"])

    # Install required packages
    subprocess.run(["py", "-m", "pip", "install", "-r", "requirements.txt"])

    # Install spaCy model
    try:
        subprocess.run(["py", "-m", "spacy", "download", "en_core_web_trf"])
    except:
        print("Note: You may need to install spaCy model manually with:")
        print("py -m spacy download en_core_web_trf")

    print("Packages installed successfully!")

def test_gemini_api():
    """Test the Gemini API."""
    print("Testing Gemini API...")

    # Run the test script
    result = subprocess.run(["py", "test_gemini.py"], capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print(result.stderr)
        return False

    return True

def run_app():
    """Run the Streamlit app."""
    print("Starting the Streamlit app...")

    # Run the Streamlit app
    subprocess.run(["py", "-m", "streamlit", "run", "src/app/app.py"])

if __name__ == "__main__":
    print("LAWGPT Setup and Run Script")
    print("==========================")

    # Check if .env file exists
    if not os.path.exists(".env"):
        print("Creating .env file with Google API key...")
        with open(".env", "w") as f:
            f.write("GOOGLE_API_KEY=AIzaSyBcr3Uire2ma92maQnACBPMsfuaU1MrSYg")

    # Install packages
    install_packages()

    # Test Gemini API
    if test_gemini_api():
        # Run the app
        run_app()
    else:
        print("Failed to test Gemini API. Please check your API key and try again.")

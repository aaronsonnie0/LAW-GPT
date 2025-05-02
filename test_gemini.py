import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def test_gemini_api():
    """Test the Gemini API with a simple prompt."""
    try:
        # List available models
        print("Available models:")
        for model in genai.list_models():
            print(f"- {model.name}")

        # Create a model instance (using the correct model name)
        model = genai.GenerativeModel('gemini-1.5-pro')

        # Generate a response
        response = model.generate_content("Hello, I'm testing the Gemini API. Please respond with a short greeting.")

        # Print the response
        print("API Response:")
        print(response.text)
        print("\nAPI test successful!")
        return True
    except Exception as e:
        print(f"Error testing Gemini API: {e}")
        return False

if __name__ == "__main__":
    print("Testing Gemini API...")
    print(f"API Key: {os.getenv('GOOGLE_API_KEY')[:5]}...{os.getenv('GOOGLE_API_KEY')[-5:]}")
    test_gemini_api()

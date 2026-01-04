from dotenv import load_dotenv
import os

def load_env():

    load_dotenv()

    try:
        groq_api = os.getenv('GROQ_API_KEY')
        tavily_api = os.getenv("TAVILY_API_KEY")
        print("Keys loaded successfully")
    except Exception as e:
        print("Issue loading api_keys")
        print(f"Error: {e}")    
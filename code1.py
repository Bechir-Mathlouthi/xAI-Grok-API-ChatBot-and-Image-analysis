from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

api_key = os.getenv("XAI_API_KEY")

if api_key:
    print("API Key loaded successfully.")
else:
    print("API Key is missing or not loaded.")
print("Loaded API Key:", api_key)

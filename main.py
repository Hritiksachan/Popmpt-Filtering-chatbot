from dotenv import load_dotenv
import os

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")
print("✅ HF_API_KEY:", HF_API_KEY)

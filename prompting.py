import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"
headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}

def generate_from_huggingface(context, query):
    system_prompt = (
        "You are an expert agriculture advisor for the state of Tamil Nadu, India. "
        "Only answer queries that are specifically related to Tamil Nadu. "
        "If a user asks about other states or general advice, respond: "
        "\"I'm sorry, I can only assist with Tamil Nadu-specific agriculture queries.\""
    )

    full_prompt = f"{system_prompt}\n\nContext:\n{context}\n\nQuestion:\n{query}\nAnswer:"

    payload = {
        "inputs": full_prompt,
        "parameters": {
            "temperature": 0.4,
            "max_new_tokens": 300,
            "return_full_text": False,
        }
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()[0]['generated_text']
    else:
        return f"❌ Error: {response.status_code} - {response.text}"

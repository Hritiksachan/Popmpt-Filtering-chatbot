from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import chromadb
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["OMP_NUM_THREADS"] = "2"  # Safe thread usage

# Hugging Face API key and endpoint
HF_API_KEY = os.getenv("HF_API_KEY")
HF_API_URL = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-alpha"
headers = {
    "Authorization": f"Bearer {HF_API_KEY}",
    "Content-Type": "application/json"
}

# FastAPI app
app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load embedding model
embedding_model = SentenceTransformer("BAAI/bge-small-en")

# Connect to ChromaDB collection used by extraction script
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="doc_chunks")

# Request schema
class ChatInput(BaseModel):
    query: str

# Hugging Face inference
def generate_response(prompt):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 300,
            "temperature": 0.7,
        }
    }
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    result = response.json()
    if isinstance(result, list):
        return result[0]["generated_text"]
    return result.get("error", "Model inference failed.")

# Chat endpoint
@app.post("/chat")
async def chat(chat_input: ChatInput):
    query = chat_input.query
    embedded_query = embedding_model.encode(query).tolist()

    # Retrieve top 5 relevant chunks
    results = collection.query(
        query_embeddings=[embedded_query],
        n_results=5
    )

    # Combine chunks
    retrieved_chunks = " ".join(results["documents"][0])

    # Create prompt
    prompt = (
        f"Answer the question strictly using the following Tamil Nadu agriculture advisory data:\n\n"
        f"{retrieved_chunks}\n\n"
        f"Question: {query}\n\n"
        f"Answer:"
    )

    generated = generate_response(prompt)
    final_answer = generated.split("Answer:")[-1].strip()

    return {"response": final_answer}
# uvicorn Main1:app --host 127.0.0.1 --port 8000 --reload
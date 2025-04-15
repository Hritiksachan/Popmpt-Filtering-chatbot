import os
from docling.document_converter import DocumentConverter
import chromadb
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set safe thread limit
os.environ["OMP_NUM_THREADS"] = "2"

# Load sentence embedding model
embed_model = SentenceTransformer("BAAI/bge-small-en")

# Constants
MAX_TOKENS = 50
pdf_folder = "/Users/mac/Desktop/New folder (2)/pdf/"
output_folder = "/Users/mac/Desktop/New folder (2)/extracted/"
os.makedirs(output_folder, exist_ok=True)

# Initialize document converter and ChromaDB
converter = DocumentConverter()
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="doc_chunks")

# Text chunking
def chunk_text(text, max_tokens=MAX_TOKENS):
    sentences = sent_tokenize(text)
    chunks, current_chunk, current_length = [], [], 0

    for sentence in sentences:
        sentence_length = len(sentence.split())
        if current_length + sentence_length > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk, current_length = [sentence], sentence_length
        else:
            current_chunk.append(sentence)
            current_length += sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

# PDF processing
def process_pdfs():
    pdf_files = [f for f in os.listdir(pdf_folder) if f.endswith(".pdf")]

    for pdf_file in pdf_files:
        pdf_path = os.path.join(pdf_folder, pdf_file)
        result = converter.convert(pdf_path)

        document = result.document
        markdown_output = document.export_to_markdown()

        output_file = os.path.join(output_folder, pdf_file.replace(".pdf", ".md"))
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(markdown_output)

        with open(output_file, "r", encoding="utf-8") as f:
            document_text = f.read()

        chunks = chunk_text(document_text)

        for idx, chunk in enumerate(chunks):
            embedding = embed_model.encode(chunk).tolist()
            try:
                collection.add(
                    ids=[f"{pdf_file}_{idx}"],
                    embeddings=[embedding],
                    documents=[chunk],
                    metadatas=[{"filename": pdf_file, "chunk_index": idx}]
                )
            except Exception as e:
                print(f"⚠️ Skipping duplicate ID {pdf_file}_{idx}: {e}")

        print(f"✅ Successfully processed {pdf_file} with {len(chunks)} chunks.")

    print(f"✅ Successfully stored text segments from {len(pdf_files)} PDFs in ChromaDB!")

if __name__ == "__main__":
    process_pdfs()

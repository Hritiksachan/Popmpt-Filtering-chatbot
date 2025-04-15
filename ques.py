from extraction import *
def retrieve_relevant_chunks(query, top_k=5):
    query_embedding = embed_model.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    return [doc for doc in results["documents"][0] if doc.strip()]


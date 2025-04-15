
from prompting import *
from ques import *
def rag_chatbot(query):
    chunks = retrieve_relevant_chunks(query)
    context = "\n".join(chunks)
    return generate_from_huggingface(context, query)

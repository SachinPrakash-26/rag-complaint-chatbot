from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os

PERSIST_DIR = "./chatbot/chroma_db"

# Load vector DB (build if not exists)
def load_vectorstore():
    if not os.path.exists(PERSIST_DIR):
        loader = PyPDFLoader("knowledge.pdf")  # Ensure this file is in your root folder
        pages = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        docs = splitter.split_documents(pages)
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = Chroma.from_documents(docs, embedding=embeddings, persist_directory=PERSIST_DIR)
        vectordb.persist()
    else:
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vectordb = Chroma(persist_directory=PERSIST_DIR, embedding_function=embeddings)
    return vectordb

vectordb = load_vectorstore()

# Real RAG-based answer
def ask_rag_question(query):
    from langchain_community.vectorstores import Chroma
    from langchain_community.embeddings import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory="./chatbot/chroma_db", embedding_function=embeddings)

    # Use diversity-based search
    results = vectordb.max_marginal_relevance_search(query, k=3)
    return "\n\n".join([doc.page_content for doc in results])


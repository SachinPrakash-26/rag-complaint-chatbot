from chatbot.rag import load_knowledge_base, ask_rag_question

# Load the knowledge base
vectordb = load_knowledge_base("chatbot/knowledge.pdf")

# Ask a test question
query = "How can I register a complaint?"
response = ask_rag_question(query, vectordb)

print("Answer:\n", response)

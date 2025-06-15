import re
import requests
from chatbot.rag import ask_rag_question, load_knowledge_base

API_BASE = "http://127.0.0.1:8000"
vectordb = load_knowledge_base("./chatbot/knowledge.pdf")

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_phone(phone):
    return re.match(r"^\d{10}$", phone)

def handle_chat(user_input, session):
    # --- Initialize required keys ---
    session.setdefault("name", None)
    session.setdefault("phone_number", None)
    session.setdefault("email", None)
    session.setdefault("complaint_details", None)

    # --- Complaint ID retrieval flow ---
    match = re.search(r"(complaint\s+)?(id\s*[:\-]?\s*)?([A-Za-z0-9\-]{6,})", user_input, re.IGNORECASE)
    if "show details" in user_input.lower() and match:
        complaint_id = match.group(3)
        response = requests.get(f"{API_BASE}/complaints/{complaint_id}")
        if response.status_code == 200:
            data = response.json()
            return (
                f"Complaint ID: {data['complaint_id']}\n"
                f"Name: {data['name']}\n"
                f"Phone: {data['phone_number']}\n"
                f"Email: {data['email']}\n"
                f"Details: {data['complaint_details']}\n"
                f"Created At: {data['created_at']}"
            )
        else:
            return "Sorry, I couldn't find that complaint ID."

    # --- Complaint creation flow ---
    if session.get('complaint_details') is None and any(word in user_input.lower() for word in ['complaint', 'not working', 'issue', 'problem', 'error']):
        session['complaint_details'] = user_input
        return "I'm sorry to hear that. Please provide your name."

    if session['complaint_details'] and not session['name']:
        session['name'] = user_input
        return "Thanks. What's your phone number?"

    if session['name'] and not session['phone_number']:
        if is_valid_phone(user_input):
            session['phone_number'] = user_input
            return "Got it. Please provide your email address."
        else:
            return "Please enter a valid 10-digit phone number."

    if session['phone_number'] and not session['email']:
        if is_valid_email(user_input):
            session['email'] = user_input
        else:
            return "That doesn't look like a valid email. Please try again."

        # All data is collected, submit complaint
        payload = {
            "name": session.get("name",""),
            "phone_number": session['phone_number'],
            "email": session['email'],
            "complaint_details": session['complaint_details']
        }
        response = requests.post(f"{API_BASE}/complaints", json=payload)
        if response.status_code == 200:
            complaint_id = response.json().get("complaint_id", "UNKNOWN")
            session.clear()  # reset for next user flow
            return f"Your complaint has been registered with ID: {complaint_id}. You'll hear back soon."
        else:
            return "There was a problem submitting your complaint. Please try again."

    # --- Fallback to RAG ---
    return ask_rag_question(user_input, vectordb)

def chatbot_response(user_input, session):
    return handle_chat(user_input, session)

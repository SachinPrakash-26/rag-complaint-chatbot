import streamlit as st
from chatbot.chatbot import chatbot_response

st.set_page_config(page_title="Complaint RAG Chatbot")
st.title(" Complaint Support Chatbot")

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session" not in st.session_state:
    st.session_state.session = {
        "name": None,
        "phone_number": None,
        "email": None,
        "complaint_details": None
    }

# Chat input box
user_input = st.chat_input("Ask a question or report a complaint:")

# Process input
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    try:
        bot_response = chatbot_response(user_input, st.session_state.session)
    except Exception as e:
        bot_response = f" Error: {str(e)}"
    st.session_state.chat_history.append(("bot", bot_response))

# --- Display chat history ---
for sender, msg in st.session_state.chat_history:
    if sender == "user":
        st.markdown(f"**You:** {msg}")
    else:
        st.markdown(f"**Bot:** {msg}")

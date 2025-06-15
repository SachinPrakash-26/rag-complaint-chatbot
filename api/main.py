from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from datetime import datetime
from chatbot.chatbot import handle_chat
from crud import get_complaint_by_id
from database import Complaint, SessionLocal

app = FastAPI()
session_store = {}

class ChatRequest(BaseModel):
    user_id: str
    message: str

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    user_id = request.user_id
    message = request.message

    if user_id not in session_store:
        session_store[user_id] = {}

    response = handle_chat(message, session_store[user_id])
    return {"response": response}

class ComplaintRequest(BaseModel):
    name: str
    phone_number: str
    email: EmailStr
    complaint_details: str

@app.post("/complaints")
def create_complaint_api(complaint: ComplaintRequest):
    db = SessionLocal()
    complaint_id = str(uuid4())
    db_complaint = Complaint(
        complaint_id=complaint_id,
        name=complaint.name,
        phone_number=complaint.phone_number,
        email=complaint.email,
        complaint_details=complaint.complaint_details,
        created_at=datetime.utcnow()
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    db.close()
    return {"complaint_id": complaint_id, "message": "Complaint created successfully"}

@app.get("/complaints/{complaint_id}")
def get_complaint_api(complaint_id: str):
    db = SessionLocal()
    complaint = get_complaint_by_id(db, complaint_id)
    db.close()
    if complaint is None:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return {
        "complaint_id": complaint.complaint_id,
        "name": complaint.name,
        "phone_number": complaint.phone_number,
        "email": complaint.email,
        "complaint_details": complaint.complaint_details,
        "created_at": complaint.created_at
    }


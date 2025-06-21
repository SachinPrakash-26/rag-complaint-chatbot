from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from uuid import uuid4
from datetime import datetime
from typing import Dict
from sqlalchemy.orm import Session

from chatbot.chatbot import handle_chat
from crud import get_complaint_by_id
from database import Complaint, SessionLocal

# FastAPI app instance
app = FastAPI()

# Enable CORS (adjust allow_origins in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update this to frontend domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
session_store: Dict[str, Dict] = {}

# Request Models
class ChatRequest(BaseModel):
    user_id: str
    message: str

class ComplaintRequest(BaseModel):
    name: str
    phone_number: str
    email: EmailStr
    complaint_details: str

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Health check
@app.get("/health")
def health_check():
    return {"status": "ok"}

# Chat endpoint
@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    user_id = request.user_id
    message = request.message

    if user_id not in session_store:
        session_store[user_id] = {}

    response = handle_chat(message, session_store[user_id])
    return {"response": response}

# Create a new complaint
@app.post("/complaints")
def create_complaint_api(complaint: ComplaintRequest, db: Session = Depends(get_db)):
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
    return {
        "complaint_id": complaint_id,
        "message": "Complaint created successfully"
    }

# Get complaint by ID
@app.get("/complaints/{complaint_id}")
def get_complaint_api(complaint_id: str, db: Session = Depends(get_db)):
    complaint = get_complaint_by_id(db, complaint_id)
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

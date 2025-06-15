from pydantic import BaseModel, EmailStr
from datetime import datetime

class ComplaintCreate(BaseModel):
    name: str
    phone_number: str
    email: EmailStr
    complaint_details: str

class ComplaintOut(ComplaintCreate):
    complaint_id: str
    created_at: datetime



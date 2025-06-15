from database import Complaint, SessionLocal

def create_complaint(data: dict):
    db = SessionLocal()
    complaint = Complaint(**data)
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    db.close()
    return complaint

def get_complaint_by_id(db, complaint_id: str):
    return db.query(Complaint).filter_by(complaint_id=complaint_id).first()



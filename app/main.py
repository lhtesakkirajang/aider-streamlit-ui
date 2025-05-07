from fastapi import FastAPI, HTTPException
from app.database import SessionLocal, engine
from app.models.candidate import Candidate, Base
from app.schemas.candidate import CandidateCreate, CandidateOut
from app.crud.candidate_crud import get_candidate, create_candidate, update_candidate, delete_candidate, get_candidates

# Create the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/candidates/", response_model=CandidateOut)
def create_candidate_endpoint(candidate: CandidateCreate):
    db = SessionLocal()
    try:
        db_candidate = create_candidate(db, candidate)
        return db_candidate
    finally:
        db.close()

@app.get("/candidates/", response_model=list[CandidateOut])
def read_candidates():
    db = SessionLocal()
    try:
        return get_candidates(db)
    finally:
        db.close()

@app.get("/candidates/{candidate_id}", response_model=CandidateOut)
def read_candidate(candidate_id: int):
    db = SessionLocal()
    try:
        db_candidate = get_candidate(db, candidate_id)
        if not db_candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return db_candidate
    finally:
        db.close()

@app.put("/candidates/{candidate_id}", response_model=CandidateOut)
def update_candidate_endpoint(candidate_id: int, candidate: CandidateCreate):
    db = SessionLocal()
    try:
        db_candidate = update_candidate(db, candidate_id, candidate)
        if not db_candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return db_candidate
    finally:
        db.close()

@app.delete("/candidates/{candidate_id}")
def delete_candidate_endpoint(candidate_id: int):
    db = SessionLocal()
    try:
        result = delete_candidate(db, candidate_id)
        if not result:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return {"detail": "Candidate deleted"}
    finally:
        db.close()

from pydantic import BaseModel, EmailStr

class CandidateBase(BaseModel):
    name: str
    email: EmailStr
    phone: str = None

class CandidateCreate(CandidateBase):
    pass

class CandidateUpdate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int

    class Config:
        orm_mode = True

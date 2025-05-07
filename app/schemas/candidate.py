from pydantic import BaseModel

class CandidateBase(BaseModel):
    name: str
    email: str
    phone: str

class CandidateCreate(CandidateBase):
    pass

class CandidateOut(CandidateBase):
    id: int

    class Config:
        orm_mode = True

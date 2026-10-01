from fastapi import FastAPI
from models import User, UserPublic, UserCreate
from database import SessionDep

app = FastAPI()

@app.get("/")
async def root():
    return {"ok": True}

@app.post("/users/", response_model=UserPublic)
async def create_user(user: UserCreate, session: SessionDep):
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
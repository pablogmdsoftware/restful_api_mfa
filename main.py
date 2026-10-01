from fastapi import FastAPI, Query, HTTPException
from sqlmodel import select
from typing import Annotated
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

@app.get("/users/", response_model=list[UserPublic])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.get("/users/{user_id}", response_model=UserPublic)
def read_users(
    user_id: int,
    session: SessionDep,
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Hero not found")
    return user
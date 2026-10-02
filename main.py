from fastapi import FastAPI, Query, HTTPException
from sqlmodel import select
from typing import Annotated
from models import User, UserPublic, UserCreate, UserUpdate
from database import SessionDep
from utils import hash_password

app = FastAPI()

@app.get("/")
async def root():
    return {"ok": True}

@app.post("/users/", response_model=UserPublic)
async def create_user(user: UserCreate, session: SessionDep):
    user.password = hash_password(user.password)
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
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.patch("/users/{user_id}", response_model=UserPublic)
def update_user(
    user_id: int,
    user: UserUpdate,
    session: SessionDep
):
    user_db = session.get(User, user_id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    return user_db

@app.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    session: SessionDep
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}
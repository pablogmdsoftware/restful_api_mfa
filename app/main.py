import pyotp
import qrcode
import io
from fastapi import FastAPI, Response, HTTPException, status, Query, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from datetime import timedelta
from typing import Annotated
from models import User, UserPublic, UserCreate, UserUpdate, Token
from database import SessionDep
from utils import authenticate_user, create_access_token, get_current_user
from utils import create_hashed_topt_secret, hash_password
from utils import ACCESS_TOKEN_EXPIRE_MINUTES

app = FastAPI()

@app.get("/", tags=["Health Check"])
async def root():
    return {"ok": True}

@app.post("/token", tags=["Login"])
async def login_for_access_token(
    session: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    totp = pyotp.TOTP(user.topt_secret)
    if not totp.verify(form_data.client_secret):
        raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect topt code",
                headers={"WWW-Authenticate": "Bearer"},
            )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.mail}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")

@app.post("/users/", response_model=UserPublic, tags=["Login"])
async def create_user(user: UserCreate, session: SessionDep):
    user.password = hash_password(user.password)
    db_user = User.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@app.patch("/users/me/topt/", tags=["TOPT Token"])
def create_topt_secret(
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    user_db = session.get(User, current_user.id)
    if not user_db:
        raise HTTPException(status_code=404, detail="User not found")
    user_db.topt_secret = create_hashed_topt_secret()
    session.add(user_db)
    session.commit()
    session.refresh(user_db)
    totp = pyotp.TOTP(user_db.topt_secret)
    uri = totp.provisioning_uri(
        name=current_user.mail,
        issuer_name="Restful API"
    )
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

@app.get("/users/", response_model=list[UserPublic], tags=["Read Database"])
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
):
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.get("/users/{user_id}", response_model=UserPublic, tags=["Read Database"])
def read_users(
    user_id: int,
    session: SessionDep,
):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.get("/users/me/", response_model=UserPublic, tags=["Manage User"])
async def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user

@app.get("/users/me/topt/", tags=["TOPT Token"])
async def get_topt_qr(
    current_user: Annotated[User, Depends(get_current_user)],
):
    totp = pyotp.TOTP(current_user.topt_secret)
    uri = totp.provisioning_uri(
        name=current_user.mail,
        issuer_name="Restful API"
    )
    img = qrcode.make(uri)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")

@app.patch("/users/{user_id}", response_model=UserPublic, tags=["Manage User"])
def update_user(
    user_id: int,
    user: UserUpdate,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    if user_id == current_user.id:
        user_db = session.get(User, user_id)
        if not user_db:
            raise HTTPException(status_code=404, detail="User not found")
        user_data = user.model_dump(exclude_unset=True)
        user_db.sqlmodel_update(user_data)
        session.add(user_db)
        session.commit()
        session.refresh(user_db)
        return user_db
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")

@app.delete("/users/{user_id}", tags=["Manage User"])
def delete_user(
    user_id: int,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)],
):
    if user_id == current_user.id:    
        user = session.get(User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        session.delete(user)
        session.commit()
        return {"ok": True}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
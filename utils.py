from sqlmodel import select
from pwdlib import PasswordHash
from database import SessionDep
from models import User

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

def hash_password(password):
    return password_hash.hash(password)

def verify_password(password, hash):
    return password_hash.verify(password, hash)

def get_user(session: SessionDep, email: str) -> User:
    statement = select(User).where(User.mail == email)
    user = session.exec(statement).first()
    return user

def authenticate_user(session: SessionDep, mail: str, password: str):
    user = get_user(session, mail)
    if not user:
        verify_password(password, DUMMY_HASH)
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
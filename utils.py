from sqlmodel import select
from pwdlib import PasswordHash
from database import SessionDep
from models import User

password_hash = PasswordHash.recommended()

def hash_password(password):
    return password_hash.hash(password)

def get_user(session: SessionDep, email: str) -> User:
    statement = select(User).where(User.mail == email)
    user = session.exec(statement).first()
    return user
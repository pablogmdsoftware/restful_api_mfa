from sqlmodel import SQLModel, Field
from pydantic import BaseModel
from datetime import datetime, timezone
from database import engine

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
class UserBase(SQLModel):
    name: str = Field(index=True)
    mail: str = Field(index=True, unique=True)

class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    joined_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    topt_secret: str | None = Field(default=None)
    password: str

class UserCreate(UserBase):
    password: str

class UserPublic(UserBase):
    id: int | None
    joined_at: datetime

class UserUpdate(UserBase):
    pass

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    mail: str | None = None
from sqlmodel import SQLModel, Field
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

class UserCreate(UserBase):
    pass

class UserPublic(User):
    pass

class UserUpdate(UserBase):
    pass
from sqlmodel import SQLModel, Field
from datetime import datetime

class UserBase(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    mail: str = Field(index=True, unique=True)
    joined_at: datetime = Field(default_factory=datetime.now)
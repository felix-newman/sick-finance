from sqlmodel import Field, SQLModel
from uuid import UUID

class Source(SQLModel, table=True):
    id: UUID = Field(default_factory=UUID, primary_key=True)
    url: str = Field(default="")
    
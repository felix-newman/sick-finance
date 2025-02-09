from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

class SourceArticleBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    url: str = Field(nullable=False)
    accessed_timestamp: datetime = Field(nullable=False, default_factory=datetime.now)
    published_timestamp: datetime = Field(nullable=False, default_factory=datetime.now)
    content: str = Field(nullable=False)

class SourceArticle(SourceArticleBase, table=True):
    __tablename__ = "source_article"
    generated_articles: List["GeneratedArticle"] = Relationship(
        back_populates="source",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"},
    )

class GeneratedArticleBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    created_at: datetime = Field(default_factory=datetime.now)

    source_id: UUID = Field(foreign_key="source_article.id")

    title: str = Field(nullable=False)
    content: str = Field(nullable=False)
    lead: str = Field(nullable=False)

    mentioned_stocks: list[str] = Field(sa_column=Column(JSON))
    image_url: str = Field(nullable=True)
    image_data: str = Field(nullable=True)


class GeneratedArticle(GeneratedArticleBase, table=True):
    __tablename__ = "generated_article"


    source: SourceArticle = Relationship(back_populates="generated_articles", sa_relationship_kwargs={"lazy": "selectin"})



class GeneratedArticleRead(GeneratedArticleBase):
    source_url: Optional[str] = None  # Now this field is optional

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj: GeneratedArticle) -> "GeneratedArticleRead":
        data = GeneratedArticleBase.from_orm(obj).dict()  # or super().from_orm(obj).dict()
        data["source_url"] = obj.source.url if obj.source else None
        return cls(**data)
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy import Column, JSON
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class SourceArticleBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    url: str = Field(nullable=False)
    accessed_timestamp: datetime = Field(nullable=False)
    published_timestamp: datetime = Field(nullable=False)
    content: str = Field(nullable=False)


class SourceArticle(SourceArticleBase, table=True):
    __tablename__ = "source_article"

    generated_articles: list["GeneratedArticle"] = Relationship(
        back_populates="source",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
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

class GeneratedArticle(GeneratedArticleBase, table=True):
    __tablename__ = "generated_article"

    source: SourceArticle = Relationship(back_populates="generated_articles")



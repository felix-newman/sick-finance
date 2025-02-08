from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from src.models.articles import SourceArticle


class RestackTaskBase(SQLModel):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    status: str = Field(nullable=False)

    run_id: UUID = Field(nullable=False)
    workflow_id: UUID = Field(nullable=False)

    article_id: UUID = Field(nullable=False, foreign_key="source_article.id")


class RestackTask(RestackTaskBase, table=True):
    __tablename__ = "restack_task"

    article: SourceArticle = Relationship()

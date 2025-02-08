from sqlmodel import Session, select
from src.models.articles import SourceArticle, SourceArticleBase
from uuid import UUID
from typing import Optional


class SourceArticleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, source_article: SourceArticleBase) -> SourceArticle:
        source_article = SourceArticle(**source_article.model_dump())
        self.session.add(source_article)
        self.session.commit()
        self.session.refresh(source_article)
        return source_article

    def get(self, id: UUID) -> Optional[SourceArticle]:
        return self.session.exec(
            select(SourceArticle).where(SourceArticle.id == id)
        ).first()

    def get_all(self) -> list[SourceArticle]:
        return list(self.session.exec(select(SourceArticle)).all())

    def update(self, source_article: SourceArticle) -> SourceArticle:
        self.session.add(source_article)
        self.session.commit()
        self.session.refresh(source_article)
        return source_article

    def delete(self, id: UUID) -> None:
        source_article = self.get(id)
        if source_article:
            self.session.delete(source_article)
            self.session.commit()

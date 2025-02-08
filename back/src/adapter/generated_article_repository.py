from sqlmodel import Session, select
from src.models.articles import GeneratedArticle, GeneratedArticleBase
from uuid import UUID
from typing import Optional

class GeneratedArticleRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(self, generated_article: GeneratedArticleBase) -> GeneratedArticle:
        generated_article = GeneratedArticle(**generated_article.model_dump())
        self.session.add(generated_article)
        self.session.commit()
        self.session.refresh(generated_article)
        return generated_article

    def get(self, id: UUID) -> Optional[GeneratedArticle]:
        return self.session.exec(select(GeneratedArticle).where(GeneratedArticle.id == id)).first()

    def get_all(self) -> list[GeneratedArticle]:
        return list(self.session.exec(select(GeneratedArticle)).all())

    def update(self, generated_article: GeneratedArticle) -> GeneratedArticle:
        self.session.add(generated_article)
        self.session.commit()
        self.session.refresh(generated_article)
        return generated_article

    def delete(self, id: UUID) -> None:
        generated_article = self.get(id)
        if generated_article:
            self.session.delete(generated_article)
            self.session.commit()
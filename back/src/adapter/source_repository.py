from typing import Optional, Sequence
from sqlmodel import Session, select
from src.models.source import Source

class SourceRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def save(self, source: Source) -> Source:
        self.session.add(source)
        self.session.commit()
        self.session.refresh(source)
        return source
    
    def get_all(self) -> Sequence[Source]:
        statement = select(Source)
        return self.session.exec(statement).all()
    
    def get_by_url(self, url: str) -> Optional[Source]:
        statement = select(Source).where(Source.url == url)
        return self.session.exec(statement).first()
    
    def get_by_id(self, id: int) -> Optional[Source]:
        return self.session.get(Source, id)

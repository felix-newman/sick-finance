# main.py

import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Annotated, Any, Dict, List
from uuid import UUID
from fastapi import Depends, FastAPI, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine

from src.dummy_repository import DummyModel, DummyRepository
from src.models.articles import GeneratedArticleBase, SourceArticle, SourceArticleBase, GeneratedArticle
from src.adapter.source_article_repository import SourceArticleRepository
from src.adapter.generated_article_repository import GeneratedArticleRepository
from src.adapter.extract_articles import extract_source_articles, ArticleContent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sqlite_file_name = "database.db"
if os.getenv("ENV") == "production":
    sqlite_file_name = "/app/database.db"
    logger.info("Running in production mode")
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session




SessionDep = Annotated[Session, Depends(get_session)]

def source_article_repository(session: SessionDep):
    return SourceArticleRepository(session)

def generated_article_repository(session: SessionDep):
    return GeneratedArticleRepository(session)

source_article_repository_dep = Annotated[SourceArticleRepository, Depends(source_article_repository)]
generated_article_repository_dep = Annotated[GeneratedArticleRepository, Depends(generated_article_repository)]



@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("Started application")

@app.get("/status")
async def main():
    return {"status": "OK"}

class DummyModelRequest(BaseModel):
    name: str

@app.get("/dummies")
async def list_dummies(session: SessionDep):
    repo = DummyRepository(session)
    return repo.get_all()

@app.get("/generated_articles")
async def list_generated_articles(generated_article_repository: generated_article_repository_dep):
    return generated_article_repository.get_all()


@app.post("/generated_articles")
async def create_generated_article(
    article: GeneratedArticleBase,
    generated_article_repository: generated_article_repository_dep
) -> GeneratedArticle:
    return generated_article_repository.create(article)


@app.post("/source_articles")
async def create_source_article(
    article: SourceArticleBase, 
    source_article_repository: source_article_repository_dep
    ):
    return source_article_repository.create(article)

@app.post("/dummies")
async def create_dummy(data: DummyModelRequest, session: SessionDep):
    repo = DummyRepository(session)
    return repo.create(DummyModel(name=data.name))

@app.get("/dummies/{dummy_id}")
async def get_dummy(dummy_id: uuid.UUID, session: SessionDep) -> DummyModel:
    repo = DummyRepository(session)
    dummy = repo.get(dummy_id)
    if not dummy:
        raise HTTPException(status_code=404, detail="Item not found")
    return dummy

@app.put("/dummies/{dummy_id}")
async def update_dummy(dummy_id: uuid.UUID, data: DummyModel, session: SessionDep):
    repo = DummyRepository(session)
    if repo.get(dummy_id) is None:
        raise HTTPException(status_code=404, detail="Item not found")
    repo.update(data)

@app.delete("/dummies/{dummy_id}")
async def delete_dummy(dummy_id: uuid.UUID, session: SessionDep):
    repo = DummyRepository(session)
    repo.delete(dummy_id)


class SourceArticleRequest(BaseModel):
    url: str

@app.put("/articles/")
async def extract(source_article: SourceArticleRequest) -> List[SourceArticleBase]:
    return extract_source_articles(source_article.url)

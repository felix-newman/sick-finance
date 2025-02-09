# main.py

import logging
import os
import uuid
import time
import base64  

from contextlib import asynccontextmanager
from typing import Annotated, Any, Dict, List
from uuid import UUID
from fastapi import Depends, FastAPI, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine
import requests
from src.dummy_repository import DummyModel, DummyRepository
from src.models.articles import (
    GeneratedArticleBase,
    SourceArticle,
    SourceArticleBase,
    GeneratedArticle,
    GeneratedArticleRead
)
from src.adapter.source_article_repository import SourceArticleRepository
from src.adapter.generated_article_repository import GeneratedArticleRepository
from src.adapter.extract_articles import extract_source_articles, ArticleContent
from src.adapter.restack_controller import RestackController

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sqlite_file_name = "database.db"
if os.getenv("ENV") == "production":
    sqlite_file_name = "/app/database.db"
    logger.info("Running in production mode")
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, pool_size=10)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.close()


SessionDep = Annotated[Session, Depends(get_session)]


def source_article_repository(session: SessionDep):
    return SourceArticleRepository(session)


def generated_article_repository(session: SessionDep):
    return GeneratedArticleRepository(session)


def restack_controller(session: SessionDep):
    return RestackController(
        endpoint="https://reuk9qp3.clj5khk.gcp.restack.it", session=session
    )


source_article_repository_dep = Annotated[
    SourceArticleRepository, Depends(source_article_repository)
]
generated_article_repository_dep = Annotated[
    GeneratedArticleRepository, Depends(generated_article_repository)
]
restack_controller_dep = Annotated[RestackController, Depends(restack_controller)]


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
async def list_generated_articles(
    generated_article_repository: generated_article_repository_dep,
    background_tasks: BackgroundTasks,
        restack_controller: restack_controller_dep,
) -> List[GeneratedArticleRead]:
    if not background_tasks.tasks:
        logger.info("Starting background task")
        background_tasks.add_task(process_tasks_async, restack_controller, generated_article_repository)
    else:
        logger.info("Background task already running")
    return [GeneratedArticleRead.from_orm(g) for g in generated_article_repository.get_all()]

@app.get("/generated_articles/{title}")
async def get_generated_article(
    title: str,
    generated_article_repository: generated_article_repository_dep,
) -> GeneratedArticleRead:

    return GeneratedArticleRead.from_orm(generated_article_repository.get_by_title(title))


# New function to process tasks in a background thread
def process_tasks_async(restack_controller, generated_article_repository):
    tasks = restack_controller.get_all_running_tasks()
    for task in tasks:
        logger.info(f"Processing task {task.run_id}")
        try:
            response = restack_controller.poll_task_finished(task)
        except Exception as e:
            logger.error(f"Task poll failed {e}")
            continue
        
        if response.status_code != 200:
            logger.info(f"Task poll failed {response.status_code} {response.text}")
            # todo delete task here
            continue

        data = response.json()

        image_url = data["image_url"]
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            image_data = base64.b64encode(image_response.content).decode('utf-8')
        else:
            image_data = None
            logger.error(f"Failed to download image from {image_url}")
        generated_article = GeneratedArticleBase(
            source_id=task.article_id,
            title=data["title"],
            content=data["content"],
            lead=data["lead"],
            mentioned_stocks=data["mentioned_stocks"],
            image_url=image_url,
            image_data=image_data,
        )
        restack_controller.finish_task(task)
        generated_article_repository.create(generated_article)


@app.post("/generated_articles")
async def create_generated_article(
    article: GeneratedArticleBase,
    generated_article_repository: generated_article_repository_dep,
) -> GeneratedArticle:
    return generated_article_repository.create(article)


@app.post("/source_articles")
async def create_source_article(
    article: SourceArticleBase, source_article_repository: source_article_repository_dep
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
async def extract(
    source_article: SourceArticleRequest,
    restack_controller: restack_controller_dep,
    source_article_repository: source_article_repository_dep,
    generated_article_repository: generated_article_repository_dep,
) -> List[SourceArticleBase]:
    extracted = await extract_source_articles(source_article.url)
    logger.info(f"Extracted {len(extracted)} articles")
    repo = source_article_repository
    saved = [repo.create(article) for article in extracted]

    for article in saved:
        restack_controller.create_task(article.content, article.id)

    logger.info(f"Saved {len(saved)} articles")
    return saved

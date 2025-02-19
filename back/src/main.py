# main.py

import logging
import os
import uuid
import time
import base64
from urllib.parse import unquote  # added import

from contextlib import asynccontextmanager
from typing import Annotated, Any, Dict, List, Optional
from uuid import UUID
from fastapi import Depends, FastAPI, File, HTTPException, BackgroundTasks
from fastapi import Depends, FastAPI, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlmodel import Session, SQLModel, create_engine
import requests

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
from src.models.source import Source
from src.adapter.source_repository import SourceRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sqlite_file_name = "database.db"
if os.getenv("ENV") == "production":
    sqlite_file_name = "/app/database.db"
    logger.info("Running in production mode")
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args, pool_size=10)


class SourceArticleRequest(BaseModel):
    url: str


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


def source_repository(session: SessionDep):
    return SourceRepository(session)


source_article_repository_dep = Annotated[
    SourceArticleRepository, Depends(source_article_repository)
]
generated_article_repository_dep = Annotated[
    GeneratedArticleRepository, Depends(generated_article_repository)
]
restack_controller_dep = Annotated[RestackController, Depends(restack_controller)]
source_repository_dep = Annotated[SourceRepository, Depends(source_repository)]

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


@app.get("/sources")
async def list_sources(
    source_repository: source_repository_dep,
) -> List[Source]:
    return source_repository.get_all()


@app.put("/sources")
async def create_source(
    source: SourceArticleRequest,
    source_repository: source_repository_dep,
) -> None:
    _ = source_repository.save(Source(url=source.url, id=uuid.uuid4()))
    return None


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
    title = unquote(title)  # decode escaped title from URI
    logger.info(f"Getting article with title {title}")
    article = generated_article_repository.get_by_title(title)
    if not article:
        raise HTTPException(status_code=404, detail="Item not found")
    return GeneratedArticleRead.from_orm(article)


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

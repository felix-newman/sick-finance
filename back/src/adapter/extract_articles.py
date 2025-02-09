import os
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from dotenv import load_dotenv
from src.models.articles import SourceArticleBase
import logging
from datetime import datetime
import asyncio  # added import for asynchronous support

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NestedModel1(BaseModel):
    title: str
    date_published: str
    author: Optional[str] = None
    content: str
    url: str


class ExtractSchema(BaseModel):
    articles: list[NestedModel1]


class ArticleContent(BaseModel):
    article_content: str


load_dotenv()
app = FirecrawlApp(api_key=os.environ.get("FIRECRAWL_API_KEY"))


async def fetch_article(article: NestedModel1, i: int, total: int) -> SourceArticleBase:
    logger.info("Extracting the full content of the article. %s in %s", i, total)
    article_result = await asyncio.to_thread(
        app.extract,
        [article.url],
        {
            "prompt": "Extract the full content of the article from the specified URL.",
            "schema": ArticleContent.model_json_schema(),
        },
    )
    content = ArticleContent(**article_result["data"])
    logger.info("data scraped content len %s", len(content.article_content))
    return SourceArticleBase(
        accessed_timestamp=datetime.now(),
        published_timestamp=datetime.now(),
        url=article.url,
        content=content.article_content,
    )

async def extract_source_articles(url: str) -> List[SourceArticleBase]:
    try:
        logger.info(f"Extracting articles from the first page of the {url}.")
        page_response = await asyncio.to_thread(
            app.extract,
            [url],
            {
                "prompt": "Extract all articles including their title, date published, author, content, and URL.",
                "schema": ExtractSchema.model_json_schema(),
            },
        )
        article_response: ExtractSchema = ExtractSchema(**page_response["data"])
        logger.info("scraped %s", len(article_response.articles))

        tasks = []
        for i, article in enumerate(article_response.articles):
            if i == 5:
                break
            tasks.append(fetch_article(article, i, len(article_response.articles)))
        res = await asyncio.gather(*tasks)

        logger.info("Firecrawl ended returning response with %s results", len(res))
        return res
    except Exception as e:
        logger.error("Error extracting articles", e)
        return res

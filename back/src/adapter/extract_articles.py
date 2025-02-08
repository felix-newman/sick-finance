import os
# Install with pip install firecrawl-py
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List
from dotenv import load_dotenv
from src.models.articles import SourceArticleBase
import logging

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

def extract_source_articles(url: str) -> List[SourceArticleBase]:
    try:
        logger.info("Extracting articles from the first page of the newsroom.")
        page_response = app.extract(
            [url],
            {
                "prompt": "Extract all articles including their title, date published, author, content, and URL.",
                "schema": ExtractSchema.model_json_schema(),
            },
        )
        
        article_response: ExtractSchema = ExtractSchema(**page_response["data"])
        logger.info(f"scraped {len(article_response.articles)}")
        
        res = []
        for i, article in enumerate(article_response.articles):
            if i == 2:
                break
            logger.info("Extracting the full content of the article. %s in %s", i, len(article_response.articles))
            article_result = app.extract(
                [article.url],
                {
                    "prompt": "Extract the full content of the article from the specified URL.",
                    "schema": ArticleContent.model_json_schema(),
                },
            )
            content = ArticleContent(**article_result.get("data"))
        
            logger.info("data scraped content len %s", len(content.article_content))
            res.append(
                SourceArticleBase(
                    url=article.url,
                    published_timestamp=article.date_published,
                    html=content.article_content
                )
            )
        
        logger.info(f"Firecrawl ended returnnign response with {len(res)} results")
        return res
    except Exception as e:
        logger.error("Error extracting articles", e)
        return res

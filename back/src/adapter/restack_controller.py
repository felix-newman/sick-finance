import requests
from src.models.restack_task import RestackTask
from uuid import UUID
from sqlmodel import Session, select
from src.models.articles import GeneratedArticleBase
import base64  
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RestackController:
    def __init__(self, endpoint: str, session: Session):
        self.endpoint = endpoint
        self.session = session

    def create_task(self, content: str, article_id: UUID) -> RestackTask:
        response = requests.post(
            f"{self.endpoint}/api/workflows/MultistepWorkflow",
            json={"input": {"news_article": content}},
        )
        data = response.json()
        logger.info(f"Created task with data: {data}")

        task = RestackTask(
            run_id=UUID(data["runId"]),
            workflow_id=data["workflowId"],
            article_id=article_id,
            status="running",
        )

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return task

    def get_all_running_tasks(self) -> list[RestackTask]:
        return self.session.exec(
            select(RestackTask).where(RestackTask.status == "running")
        ).all()

    def poll_task_finished(self, task: RestackTask) -> GeneratedArticleBase:

        response = requests.get(
            f"{self.endpoint}/api/workflows/MultistepWorkflow/{task.workflow_id}/{task.run_id}",
            timeout=1000,
        )
        if response.status_code != 200:
            task.status = "failed"
            self.session.commit()
            self.session.refresh(task)
        
            raise TimeoutError(f"Task {task.id} timed out")

        logger.info(f"Polled task with response: {response.text}")
        data = response.json()
        logger.info(f"Polled task with data: {data}")

        task.status = "finished"
        self.session.commit()
        self.session.refresh(task)

        image_url = data["image_url"]
        # Download and encode image
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

        return generated_article

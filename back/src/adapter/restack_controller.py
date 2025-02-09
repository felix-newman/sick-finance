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

    def finish_task(self, task: RestackTask):
        task.status = "finished"
        self.session.commit()
        self.session.refresh(task)

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
        return requests.get(
            f"{self.endpoint}/api/workflows/MultistepWorkflow/{task.workflow_id}/{task.run_id}",
            timeout=2,
        )

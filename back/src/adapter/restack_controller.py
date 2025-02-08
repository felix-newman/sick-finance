import requests
from src.models.restack_task import RestackTask
from uuid import UUID
from sqlmodel import Session, select
from src.models.articles import GeneratedArticleBase


class RestackController:
    def __init__(self, endpoint: str, session: Session):
        self.endpoint = endpoint
        self.session = session

    def create_task(self, content: str, article_id: UUID) -> RestackTask:
        response = requests.post(
            f"{self.endpoint}/api/workflows/MultistepWorkflow",
            json={"news_article": content},
        )
        data = response.json()

        task = RestackTask(
            run_id=UUID(data["runId"]),
            workflow_id=UUID(data["workflowId"]),
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
            f"{self.endpoint}/api/workflows/MultistepWorkflow/",
            data={"run_id": task.run_id, "workflow_id": task.workflow_id},
            timeout=2,
        )

        data = response.json()
        generated_article = GeneratedArticleBase(
            source_id=task.article_id,
            title=data["title"],
            content=data["content"],
            lead=data["lead"],
            mentioned_stocks=data["mentioned_stocks"],
            image_url=data["image_url"],
        )

        return generated_article

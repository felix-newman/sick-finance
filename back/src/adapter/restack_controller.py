import requests
from src.models.restack_task import RestackTask

class RestackController:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def create_task(self, content: str) -> RestackTask:
        response = requests.post(
            f"{self.endpoint}/api/workflows/MultistepWorkflow",
            json={"news_article": content}
        )
        data = response.json()
        
        return RestackTask(
            run_id=data["run_id"],
            workflow_id=data["workflow_id"]
        )
    
    def poll_task_finished(self, task: RestackTask) -> bool:
        response = requests.get(
            f"{self.endpoint}/api/workflows/MultistepWorkflow/",
            data={
                "run_id": task.run_id,
                "workflow_id": task.workflow_id
            }, 
            timeout=2
        )
        try:
            return response.status_code == 200
        except requests.exceptions.Timeout:
            return False




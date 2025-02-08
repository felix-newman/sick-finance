from pydantic import BaseModel, Field
from restack_ai.workflow import workflow, import_functions, log
from datetime import timedelta

with import_functions():
    from src.functions.llm import llm, FunctionInputParams
    from src.functions.crawl import crawl

class WorkflowInputParams ( BaseModel):
    news_url: str = Field(default="https://www.globenewswire.com/newsroom")

@workflow.defn()
class MultistepWorkflow:
    @workflow.run
    async def run(self, input: WorkflowInputParams):
        log.info("MultistepWorkflow started", input=input)
        # Step 1 get article data
        article_content = await workflow.step(
            crawl,
            FunctionInputParams(
                url=input.news_url
            ),
            start_to_close_timeout=timedelta(seconds=120)
        )

        # Step 2 Generate summary with LLM 
        llm_message = await workflow.step(
            llm,
            FunctionInputParams(
                system_content=f"You are a news information assistant. Summarize the most relevant information from any news article you get",
                user_content=article_content,
                model="gpt-4o-mini"
            ),
            start_to_close_timeout=timedelta(seconds=120)
        )
        log.info("MultistepWorkflow completed", llm_message=llm_message)
        return {
            "message": llm_message,
            "article_content": article_content
        }

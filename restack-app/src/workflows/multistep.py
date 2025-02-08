from pydantic import BaseModel, Field
from restack_ai.workflow import workflow, import_functions, log
from datetime import timedelta

with import_functions():
    from src.functions.llm import llm, FunctionInputParams

class WorkflowInputParams ( BaseModel):
    news_article: str = Field(default="Test Article, Test Company, Test Price, Test Change")


@workflow.defn()
class MultistepWorkflow:
    @workflow.run
    async def run(self, input: WorkflowInputParams):
        log.info("MultistepWorkflow started", input=input)
                # Step 1 Generate summary with LLM 
        llm_summary = await workflow.step(
            llm,
            FunctionInputParams(
                system_content=f"You are a financial news analyst. Summarize the most relevant information from the news article you get send.",
                user_content=input.news_article,
                model="gpt-4o-mini"
            ),
            start_to_close_timeout=timedelta(seconds=120)
        )
        log.info("MultistepWorkflow first step completed", llm_summary=llm_summary)
        # Step 2 Generate article and image with LLM 
        llm_article = await workflow.step(
            llm,
            FunctionInputParams(
                system_content="""You are a financial news reporter. You are given a summary of financial information. 
                Generate a click bait title and a short news article from this information. The output format should be:
                {
                    "title": "<title>",
                    "article": "<article>"
                }
                """,
                user_content=llm_summary,
                model="gpt-4o-mini"
            ),
            start_to_close_timeout=timedelta(seconds=120)
        )
        log.info("MultistepWorkflow completed")
        return {
            "article_summary": llm_summary,
            "article": llm_article
        }

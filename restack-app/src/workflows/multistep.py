from pydantic import BaseModel, Field
from restack_ai.workflow import workflow, import_functions, log
from datetime import timedelta
import json
with import_functions():
    from src.functions.llm import llm, FunctionInputParams
    from src.functions.generate_image import generate_image, GenerateImageInputParams


class WorkflowInputParams(BaseModel):
    news_article: str = Field(
        default="Test Article, Test Company, Test Price, Test Change"
    )


@workflow.defn()
class MultistepWorkflow:
    @workflow.run
    async def run(self, input: WorkflowInputParams):
        log.info("MultistepWorkflow started", input=input)
        # Step 1 Generate summary with LLM 
        # Step 1 Generate summary with LLM
        llm_summary = await workflow.step(
            llm,
            FunctionInputParams(
                system_content=f"You are a financial news analyst. Summarize the most relevant information from the news article you get send.",
                user_content=input.news_article,
                model="gpt-4o-mini",
            ),
            start_to_close_timeout=timedelta(seconds=120),
        )
        log.info("MultistepWorkflow first step completed", llm_summary=llm_summary)
        # Step 2 Generate article and image with LLM
        llm_article = await workflow.step(
            llm,
            FunctionInputParams(
                system_content="""You are a financial news reporter. You are given a summary of financial information. 
                Generate a click bait title and a short news article from this information. The output must be a JSON object with the following fields:
                {
                    "title": "<title>",
                    "lead": "<lead>",
                    "content": "<content>",
                    "mentioned_stocks": ["<ticker_symbol1>", "<ticker_symbol2>", "<ticker_symbol3>"] (Can also be empty if no stocks are mentioned)
                }
                """,
                user_content=llm_summary,
                model="gpt-4o-mini",
            ),
            start_to_close_timeout=timedelta(seconds=120),
        )

        llm_image_url = await workflow.step(
            generate_image,
            GenerateImageInputParams(
                prompt=f"Generate a image for the follwoing news article: {llm_article}",
                model="dall-e-3",
                n=1,
                size="1024x1024",
            ),
            start_to_close_timeout=timedelta(seconds=120),
        )
        log.info("MultistepWorkflow completed")
        return {
            "original_summary": llm_summary,
            "image_url": llm_image_url,
            **json.loads(llm_article),
        }

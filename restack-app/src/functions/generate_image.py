from restack_ai.function import function, log, FunctionFailure
from openai import OpenAI
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass
class GenerateImageInputParams:
    prompt: str
    model: str | None = None
    n: int | None = None
    size: str | None = None

@function.defn()
async def generate_image(input: GenerateImageInputParams) -> str:
    try:
        log.info("generate_image function started", input=input)

        if (os.environ.get("RESTACK_API_KEY") is None):
            raise FunctionFailure("RESTACK_API_KEY is not set", non_retryable=True)
        
        client = OpenAI()

        response = client.images.generate(
            model=input.model or "dall-e-3",
            prompt=input.prompt,
            n=input.n or 1,
            size=input.size or "1024x1024"
        )
        log.info("generate_image function completed", response=response)
        return response.data[0].url
    except Exception as e:
        log.error("generate_image function failed", error=e)
        raise e
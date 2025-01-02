 
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from ..config import settings

class LLMManager:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0.7,
            openai_api_key=settings.OPENAI_API_KEY
        )

    async def generate_response(self, prompt: str):
        try:
            chain = LLMChain(llm=self.llm, prompt=prompt)
            return await chain.arun(input=prompt)
        except Exception as e:
            logger.error(f"LLM error: {e}")
            raise

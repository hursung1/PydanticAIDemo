import os
import logfire
import langchain

from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_ollama import ChatOllama

class CityLocation(BaseModel):
    city: str
    country: str

os.environ["LANGSMITH_TRACING"] = "true"
# logfire.configure()
# logfire.instrument_pydantic_ai()

llm = OllamaModel(
    "gpt-oss:120b-cloud", 
    provider=OllamaProvider(
        base_url="https://ollama.com/v1",
        api_key=os.environ["OLLAMA_API_KEY"]
        )
    )

agent = Agent(
    model=llm, 
    output_type=CityLocation,
    instructions="Answer precisely.")

def main():
    agent_out = agent.run_sync("I need a description about Osaka.")
    print(agent_out)


if __name__ == "__main__":
    main()

import os
import ollama
import asyncio
import logfire
import langchain
import rag_agent

from tavily import TavilyClient
from pymilvus import MilvusClient

from variables import DEFAULT_MILVUS_URI, DEFAULT_OLLAMA_HOST

os.environ["LANGSMITH_TRACING"] = "true"
# logfire.configure()
# logfire.instrument_pydantic_ai()

async def main():
    milvus_client = MilvusClient(DEFAULT_MILVUS_URI)
    ollama_client = ollama.Client(host=DEFAULT_OLLAMA_HOST)
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))

    deps = rag_agent.MyDeps(
        milvus_client=milvus_client,
        ollama_client=ollama_client,
        tavily_client=tavily_client
    )

    agent_out = await rag_agent.rag_agent.run("I need a description about Osaka.", deps=deps)
    
    return agent_out.output

if __name__ == "__main__":
    result = asyncio.run(main())
    print(result)

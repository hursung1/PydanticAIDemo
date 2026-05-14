import os
import ollama
import asyncio
import logfire

from tavily import TavilyClient
from pymilvus import MilvusClient

from rag_agent import MyDeps, rag_agent
from variables import DEFAULT_MILVUS_URI, DEFAULT_OLLAMA_HOST

os.environ["LANGSMITH_TRACING"] = "true"
# logfire.configure()
# logfire.instrument_pydantic_ai()

async def main():
    milvus_client = MilvusClient(DEFAULT_MILVUS_URI)
    ollama_client = ollama.Client(host=DEFAULT_OLLAMA_HOST)
    tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", ""))

    deps = MyDeps(
        milvus_client=milvus_client,
        ollama_client=ollama_client,
        tavily_client=tavily_client,
        documents=""
    )

    rag_result = await rag_agent.run("소프트웨어 버전관리는 어떻게 해야됨?", deps=deps)
    return rag_result.output


if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"used_tool: {result.used_tool}")
    print(f"output: {result.agent_answer}")
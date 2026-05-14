import os
import ollama

from tavily import TavilyClient
from dataclasses import dataclass
from pymilvus import MilvusClient
from pydantic_ai import Agent, RunContext
from pydantic_ai.models.ollama import OllamaModel
from pydantic_ai.providers.ollama import OllamaProvider

from variables import DEFAULT_EMBEDDING_MODEL, DEFAULT_COLLECTION_NAME

@dataclass
class MyDeps:
    ollama_client: ollama.Client
    milvus_client: MilvusClient
    tavily_client: TavilyClient

@dataclass
class OutputType:
    used_tool: str
    agent_answer: str

llm = OllamaModel(
    model_name="gpt-oss:120b-cloud",
    provider=OllamaProvider(
        base_url="https://ollama.com/v1",
        api_key=os.environ["OLLAMA_API_KEY"]
        )
    )

rag_agent = Agent(
    model=llm,
    deps_type=MyDeps,
    output_type=OutputType,
    system_prompt="찾은 문서 내용을 이용하여 사용자에게 친절하고 소상히 답변한다. 만약 주어진 문서가 없거나, 주어졌더라도 답을 찾을 수 없다면 '모른다' 라고 대답하라. 또, 검색에 사용했던 tool을 답변으로 함께 제공해야 한다."
)

# @rag_agent.system_prompt
# async def build_system_prompt(ctx: RunContext[MyDeps]) -> str:
#     return f"문서 검색 후 답변 생성 시  {ctx.deps.i}번 문서에 비중을 두고 작성하라."

@rag_agent.instructions
async def instruction() -> str:
    return ""

@rag_agent.tool
async def retrieve(ctx: RunContext[MyDeps], search_query: str) -> str:
    """
    Milvus VDB에서 문서 검색 수행
    Software Engineering에 관한 문서만 가지고 있다.

    Args:
        ctx: 호출 시 context.
        search_query: 문서 검색어
    """
    
    query_emb = ctx.deps.ollama_client.embed(model=DEFAULT_EMBEDDING_MODEL, input=search_query)
    retrieve_results = ctx.deps.milvus_client.search(
        collection_name=DEFAULT_COLLECTION_NAME, 
        data=query_emb.embeddings,
        limit=5,
        output_fields=["text"]
    )

    return "\n\n".join(
        f"# Document {i+1}\n{hit["entity"]["text"]}"
        for i, hit in enumerate(retrieve_results[0])
    )

@rag_agent.tool
async def search(ctx: RunContext[MyDeps], search_query: str) -> str:
    """
    일반적인 정보를 검색하기 위함
    WEB에서 관련 정보를 검색 (tavily API 사용)

    Args:
        ctx: 호출 시 context.
        search_query: 문서 검색어
    """
    response = ctx.deps.tavily_client.search(search_query)
    print("search response", response)
    return "\n\n".join(
        f"# Document {i+1}\nTitle: {hit['title']}\n{hit['content']}"
        for i, hit in enumerate(response.get("results"))
    )
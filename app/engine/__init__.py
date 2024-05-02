import yaml
from llama_index.core.settings import Settings
from llama_index.core.agent import AgentRunner
from llama_index.core.tools.query_engine import QueryEngineTool
from llama_index.postprocessor.colbert_rerank import ColbertRerank
from app.engine.index import get_index


def load_configs() -> dict:
    with open("config/agent.yaml") as f:
        configs = yaml.safe_load(f)
    return configs


def get_agent_runner() -> AgentRunner:
    configs = load_configs()

    system_prompt = configs["agent"].get("system_prompt", None)
    tool_name = configs["agent"].get("tool_name", "docs_search")
    tool_description = configs["agent"].get(
        "tool_description", "Useful for asking questions about a knowledge base."
    )
    verbose = configs["agent"].get("verbose", True)

    top_k = configs["index"].get("top_k", 10)
    rerank_top_n = configs["index"].get("rerank_top_n", 3)
    tools = []

    # Add query tool if index exists
    index = get_index()
    if index is not None:
        query_engine = index.as_query_engine(
            similarity_top_k=int(top_k),
            node_postprocessors=[ColbertRerank(top_n=rerank_top_n)],
        )
        query_engine_tool = QueryEngineTool.from_defaults(
            query_engine=query_engine,
            description=tool_description,
            name=tool_name,
        )
        tools.append(query_engine_tool)

    return AgentRunner.from_llm(
        llm=Settings.llm,
        tools=tools,
        system_prompt=system_prompt,
        verbose=verbose,
    )

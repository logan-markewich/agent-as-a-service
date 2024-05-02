import yaml
from typing import Optional
from llama_index.core.settings import Settings


def load_configs() -> dict:
    with open("config/settings.yaml") as f:
        configs = yaml.safe_load(f)
    return configs


def init_ollama(
    model_name: str,
    temperature: Optional[int],
    max_tokens: Optional[int],
    embed_model_name: str,
    embed_batch_size: Optional[int],
) -> None:
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.ollama import OllamaEmbedding

    Settings.embed_model = OllamaEmbedding(
        model_name=embed_model_name, embed_batch_size=embed_batch_size
    )
    Settings.llm = Ollama(
        model=model_name,
        temperature=temperature,
        max_tokens=max_tokens,
        request_timeout=3600.0,
    )


def init_openai(
    model_name: str,
    temperature: Optional[int],
    max_tokens: Optional[int],
    embed_model_name: str,
    embed_batch_size: Optional[int],
) -> None:
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding

    Settings.llm = OpenAI(
        model=model_name, temperature=temperature, max_tokens=max_tokens
    )
    Settings.embed_model = OpenAIEmbedding(
        model_name=embed_model_name, embed_batch_size=embed_batch_size
    )


def init_settings() -> None:
    configs = load_configs()

    model_provider = configs.get("model_provider")
    model_name = configs.get("model_name")
    temperature = configs.get("temperature")
    max_tokens = configs.get("max_tokens")
    embed_model_name = configs.get("embed_model_name")
    embed_batch_size = configs.get("embed_batch_size")

    assert model_name is not None
    assert embed_model_name is not None

    if model_provider == "openai":
        init_openai(
            model_name, temperature, max_tokens, embed_model_name, embed_batch_size
        )
    elif model_provider == "ollama":
        init_ollama(
            model_name, temperature, max_tokens, embed_model_name, embed_batch_size
        )
    else:
        raise ValueError(f"Invalid model provider: {model_provider}")
    Settings.chunk_size = configs.get("chunk_size", 1024)
    Settings.chunk_overlap = configs.get("chunk_overlap", 128)

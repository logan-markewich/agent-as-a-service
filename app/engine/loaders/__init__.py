import yaml
import logging
from typing import List
from app.engine.loaders.file import FileLoaderConfig, get_file_documents
from app.engine.loaders.web import WebLoaderConfig, get_web_documents
from app.engine.loaders.db import DBLoaderConfig, get_db_documents
from llama_index.core import Document

logger = logging.getLogger(__name__)


def load_configs() -> dict:
    with open("config/loaders.yaml") as f:
        configs = yaml.safe_load(f)
    return configs


def get_documents() -> List[Document]:
    documents = []
    config = load_configs()
    for loader_type, loader_config in config.items():
        logger.info(
            f"Loading documents from loader: {loader_type}, config: {loader_config}"
        )
        if loader_type == "file":
            documents = get_file_documents(FileLoaderConfig(**loader_config))
        elif loader_type == "web":
            documents = get_web_documents(WebLoaderConfig(**loader_config))
        elif loader_type == "db":
            documents = get_db_documents(
                configs=[DBLoaderConfig(**cfg) for cfg in loader_config]
            )
        else:
            raise ValueError(f"Invalid loader type: {loader_type}")
        documents.extend(documents)

    return documents

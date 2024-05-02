import logging
from typing import List
from pydantic import BaseModel
from llama_index.core import Document

logger = logging.getLogger(__name__)


class DBLoaderConfig(BaseModel):
    uri: str
    queries: List[str]


def get_db_documents(configs: List[DBLoaderConfig]) -> List[Document]:
    from llama_index.readers.database import DatabaseReader

    docs = []
    for entry in configs:
        loader = DatabaseReader(uri=entry.uri)
        for query in entry.queries:
            logger.info(f"Loading data from database with query: {query}")
            documents = loader.load_data(query=query)
            docs.extend(documents)

    return documents

from pydantic import BaseModel, Field
from typing import List
from llama_index.core import Document


class CrawlUrl(BaseModel):
    base_url: str
    prefix: str
    max_depth: int = Field(default=1, ge=0)


class WebLoaderConfig(BaseModel):
    driver_arguments: List[str] = Field(default=None)
    urls: List[CrawlUrl]


def get_web_documents(config: WebLoaderConfig) -> List[Document]:
    from llama_index.readers.web import WholeSiteReader
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    options = Options()
    driver_arguments = config.driver_arguments or []
    for arg in driver_arguments:
        options.add_argument(arg)

    docs = []
    for url in config.urls:
        scraper = WholeSiteReader(
            prefix=url.prefix,
            max_depth=url.max_depth,
            driver=webdriver.Chrome(options=options),
        )
        docs.extend(scraper.load_data(url.base_url))

    return docs

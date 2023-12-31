"""Init file of LlamaIndex."""
from pathlib import Path

with open(Path(__file__).absolute().parents[0] / "VERSION") as _f:
    __version__ = _f.read().strip()


import logging
from logging import NullHandler

from custom_llama_index.data_structs.struct_type import IndexStructType

# embeddings
from custom_llama_index.embeddings.langchain import LangchainEmbedding
from custom_llama_index.embeddings.openai import OpenAIEmbedding

# structured
from custom_llama_index.indices.common.struct_store.base import SQLDocumentContextBuilder
from custom_llama_index.indices.empty import GPTEmptyIndex

# indices
from custom_llama_index.indices.keyword_table import (
    GPTKeywordTableIndex,
    GPTRAKEKeywordTableIndex,
    GPTSimpleKeywordTableIndex,
)
from custom_llama_index.indices.list import GPTListIndex

# prompt helper
from custom_llama_index.indices.prompt_helper import PromptHelper

# for composability
from custom_llama_index.indices.query.schema import QueryConfig, QueryMode
from custom_llama_index.indices.struct_store.sql import GPTSQLStructStoreIndex
from custom_llama_index.indices.tree import GPTTreeIndex
from custom_llama_index.indices.vector_store import (
    GPTChromaIndex,
    GPTFaissIndex,
    GPTPineconeIndex,
    GPTQdrantIndex,
    GPTSimpleVectorIndex,
    GPTVectorStoreIndex,
    GPTWeaviateIndex,
)

# langchain helper
from custom_llama_index.langchain_helpers.chain_wrapper import LLMPredictor
from custom_llama_index.langchain_helpers.memory_wrapper import GPTIndexMemory
from custom_llama_index.langchain_helpers.sql_wrapper import SQLDatabase

# prompts
from custom_llama_index.prompts.base import Prompt
from custom_llama_index.prompts.prompts import (
    KeywordExtractPrompt,
    QueryKeywordExtractPrompt,
    QuestionAnswerPrompt,
    RefinePrompt,
    SummaryPrompt,
    TreeInsertPrompt,
    TreeSelectMultiplePrompt,
    TreeSelectPrompt,
)

# readers
from custom_llama_index.readers import (
    BeautifulSoupWebReader,
    ChromaReader,
    DiscordReader,
    Document,
    FaissReader,
    GithubRepositoryReader,
    GoogleDocsReader,
    JSONReader,
    MboxReader,
    NotionPageReader,
    ObsidianReader,
    PineconeReader,
    QdrantReader,
    RssReader,
    SimpleDirectoryReader,
    SimpleMongoReader,
    SimpleWebPageReader,
    SlackReader,
    StringIterableReader,
    TrafilaturaWebReader,
    TwitterTweetReader,
    WeaviateReader,
    WikipediaReader,
)
from custom_llama_index.readers.download import download_loader

# token predictor
from custom_llama_index.token_counter.mock_chain_wrapper import MockLLMPredictor
from custom_llama_index.token_counter.mock_embed_model import MockEmbedding

# best practices for library logging:
# https://docs.python.org/3/howto/logging.html#configuring-logging-for-a-library
logging.getLogger(__name__).addHandler(NullHandler())


__all__ = [
    "GPTKeywordTableIndex",
    "GPTSimpleKeywordTableIndex",
    "GPTRAKEKeywordTableIndex",
    "GPTListIndex",
    "GPTEmptyIndex",
    "GPTTreeIndex",
    "GPTFaissIndex",
    "GPTPineconeIndex",
    "GPTQdrantIndex",
    "GPTSimpleVectorIndex",
    "GPTVectorStoreIndex",
    "GPTWeaviateIndex",
    "GPTChromaIndex",
    "GPTSQLStructStoreIndex",
    "Prompt",
    "LangchainEmbedding",
    "OpenAIEmbedding",
    "SummaryPrompt",
    "TreeInsertPrompt",
    "TreeSelectPrompt",
    "TreeSelectMultiplePrompt",
    "RefinePrompt",
    "QuestionAnswerPrompt",
    "KeywordExtractPrompt",
    "QueryKeywordExtractPrompt",
    "WikipediaReader",
    "ObsidianReader",
    "Document",
    "SimpleDirectoryReader",
    "JSONReader",
    "SimpleMongoReader",
    "NotionPageReader",
    "GoogleDocsReader",
    "MboxReader",
    "SlackReader",
    "StringIterableReader",
    "WeaviateReader",
    "FaissReader",
    "ChromaReader",
    "PineconeReader",
    "QdrantReader",
    "DiscordReader",
    "SimpleWebPageReader",
    "RssReader",
    "BeautifulSoupWebReader",
    "TrafilaturaWebReader",
    "LLMPredictor",
    "MockLLMPredictor",
    "MockEmbedding",
    "SQLDatabase",
    "GPTIndexMemory",
    "SQLDocumentContextBuilder",
    "SQLContextBuilder",
    "PromptHelper",
    "QueryConfig",
    "QueryMode",
    "IndexStructType",
    "TwitterTweetReader",
    "download_loader",
    "GithubRepositoryReader",
]

# NOTE: keep for backwards compatibility
SQLContextBuilder = SQLDocumentContextBuilder

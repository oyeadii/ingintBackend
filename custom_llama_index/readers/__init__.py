"""Data Connectors for LlamaIndex.

This module contains the data connectors for LlamaIndex. Each connector inherits
from a `BaseReader` class, connects to a data source, and loads Document objects
from that data source.

You may also choose to construct Document objects manually, for instance
in our `Insert How-To Guide <../how_to/insert.html>`_. See below for the API
definition of a Document - the bare minimum is a `text` property.

"""

from custom_llama_index.readers.chroma import ChromaReader
from custom_llama_index.readers.discord_reader import DiscordReader
from custom_llama_index.readers.elasticsearch import ElasticsearchReader
from custom_llama_index.readers.faiss import FaissReader

# readers
from custom_llama_index.readers.file.base import SimpleDirectoryReader
from custom_llama_index.readers.github_readers.github_repository_reader import (
    GithubRepositoryReader,
)
from custom_llama_index.readers.google_readers.gdocs import GoogleDocsReader
from custom_llama_index.readers.json import JSONReader
from custom_llama_index.readers.make_com.wrapper import MakeWrapper
from custom_llama_index.readers.mbox import MboxReader
from custom_llama_index.readers.mongo import SimpleMongoReader
from custom_llama_index.readers.notion import NotionPageReader
from custom_llama_index.readers.obsidian import ObsidianReader
from custom_llama_index.readers.pinecone import PineconeReader
from custom_llama_index.readers.qdrant import QdrantReader
from custom_llama_index.readers.schema.base import Document
from custom_llama_index.readers.slack import SlackReader
from custom_llama_index.readers.steamship.file_reader import SteamshipFileReader
from custom_llama_index.readers.string_iterable import StringIterableReader
from custom_llama_index.readers.twitter import TwitterTweetReader
from custom_llama_index.readers.weaviate.reader import WeaviateReader
from custom_llama_index.readers.web import (
    BeautifulSoupWebReader,
    RssReader,
    SimpleWebPageReader,
    TrafilaturaWebReader,
)
from custom_llama_index.readers.wikipedia import WikipediaReader
from custom_llama_index.readers.youtube_transcript import YoutubeTranscriptReader

__all__ = [
    "WikipediaReader",
    "YoutubeTranscriptReader",
    "SimpleDirectoryReader",
    "JSONReader",
    "SimpleMongoReader",
    "NotionPageReader",
    "GoogleDocsReader",
    "DiscordReader",
    "SlackReader",
    "WeaviateReader",
    "PineconeReader",
    "QdrantReader",
    "ChromaReader",
    "FaissReader",
    "Document",
    "StringIterableReader",
    "SimpleWebPageReader",
    "BeautifulSoupWebReader",
    "TrafilaturaWebReader",
    "RssReader",
    "MakeWrapper",
    "TwitterTweetReader",
    "ObsidianReader",
    "GithubRepositoryReader",
    "MboxReader",
    "ElasticsearchReader",
    "SteamshipFileReader",
]

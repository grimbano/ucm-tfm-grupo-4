

from typing import Any, Callable, Dict, List, Optional, Union

import chromadb
from chromadb.api.collection_configuration import CreateCollectionConfiguration

from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings

from src.utils.customs import DocumentWithScore
from .base import ExtendedChromaCollection


class ExamplesChromaCollection(ExtendedChromaCollection):
    """
    A specialized ChromaDB collection designed for managing and querying
    SQL query examples.

    This class extends `ExtendedChromaCollection` to provide a dedicated
    and opinionated interface for storing and retrieving documents that
    represent pairs of user queries and their corresponding SQL queries.
    It is optimized for tasks such as few-shot learning and fine-tuning
    Language Models (LLMs) by providing a utility method to format retrieved
    documents into a structure that LLMs can readily consume.

    The class inherits all initialization parameters and core vector database
    functionality from `ExtendedChromaCollection`, while adding a specific
    static method (`format_for_llm`) to streamline the data preparation
    workflow for LLM-based applications.
    """

    @staticmethod
    def format_for_llm(
        documents: List[Union[Document, DocumentWithScore]]
    ) -> List[Dict[str, Any]]:
        """
        Prepares a list of documents for input into a Language Model.

        This method extracts specific fields from a list of documents or document-score
        tuples and formats them into a simplified list of dictionaries. The resulting
        format is typically used for fine-tuning or few-shot learning with LLMs,
        where a 'user_query' (from `page_content`) is paired with a corresponding
        'sql_query' (from `metadata`).

        The method handles two input types: a list of `Document` objects and a list of
        `DocumentWithScore` tuples. It automatically identifies the input type and
        extracts the relevant information.

        Args:
            documents: A list of `Document` objects or `DocumentWithScore` tuples.
                    The list is expected to contain only one type of object.

        Returns:
            A list of dictionaries, where each dictionary contains a 'user_query'
            and a 'sql_query' field. Empty inputs and documents without 'sql_query'
            metadata are handled gracefully, returning an empty list.
        """

        if not documents:
            return []
        
        is_document_list = isinstance(documents[0], Document)

        output_list = []
        for item in documents:
            example_dict = {}
            doc = None
            score = None

            if is_document_list:
                doc = item
            else:
                doc, score = item

            if doc.metadata:
                output_list.append({
                    'user_query': doc.page_content,
                    'sql_query': doc.metadata.get('sql_query')
                })

        return output_list


    def __init__(
        self,
        collection_name: str,
        embedding_function: Optional[Embeddings] = None,
        persist_directory: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        ssl: bool = False,
        headers: Optional[dict[str, str]] = None,
        chroma_cloud_api_key: Optional[str] = None,
        tenant: Optional[str] = None,
        database: Optional[str] = None,
        client_settings: Optional[chromadb.config.Settings] = None,
        collection_metadata: Optional[dict] = None,
        collection_configuration: Optional[CreateCollectionConfiguration] = None,
        client: Optional[chromadb.ClientAPI] = None,
        relevance_score_fn: Optional[Callable[[float], float]] = None,
        create_collection_if_not_exists: bool = True,
        reset_collection: Optional[bool] = False,
        clear_collection: Optional[bool] = False,
    ):
        """
        Initializes the ExamplesChromaCollection.

        This method forwards all arguments to the parent class, setting up the
        underlying ChromaDB collection with the specified configuration.

        Args:
            collection_name: The name of the collection to manage.
            embedding_function: The embedding function to use for document processing.
                    If not provided, the default function from the Chroma client will be used.
            persist_directory: The directory path to persist the collection. If None,
                    the collection will be ephemeral (in-memory).
            host: Hostname of a deployed Chroma server.
            port: Connection port for a deployed Chroma server. Default is 8000.
            ssl: Whether to establish an SSL connection with a deployed Chroma server.
                    Default is False.
            headers: HTTP headers to send to a deployed Chroma server.
            chroma_cloud_api_key: Chroma Cloud API key.
            tenant: Tenant ID. Required for Chroma Cloud connections.
                    Default is 'default_tenant' for local Chroma servers.
            database: Database name. Required for Chroma Cloud connections.
                    Default is 'default_database'.
            client_settings: Chroma client settings
            collection_metadata: Collection configurations.
            collection_configuration: An optional configuration object to pass when
                    creating the collection. This is ignored if `create_collection_if_not_exists` is False.
            client: Chroma client. Documentation:
                    https://docs.trychroma.com/reference/python/client
            relevance_score_fn: A function to transform raw relevance scores (e.g., cosine similarity)
                    into a desired scale.Defaults to `cosine_distance_relevance_score_fn`.
            create_collection_if_not_exists: If True, creates the collection if it doesn't
                    exist. Otherwise, it will attempt to connect to an existing collection.
            reset_collection: If True, the existing collection will be deleted and a new one will 
                    be created upon initialization. This cannot be used with `clear_collection`.
            clear_collection: If True, all documents within the collection will be deleted upon
                    initialization, but the collection itself will persist.
                    This cannot be used with `reset_collection`.

        Raises:
            ValueError: If an invalid combination of arguments is provided, such as
                    `reset_collection` and `clear_collection` being simultaneously True,
                    or attempting to reset an ephemeral collection.
            RuntimeError: If an attempt to reset the collection fails.
        """
        super().__init__(
            collection_name,
            embedding_function,
            persist_directory,
            host,
            port,
            ssl,
            headers,
            chroma_cloud_api_key,
            tenant,
            database,
            client_settings,
            collection_metadata,
            collection_configuration,
            client,
            relevance_score_fn,
            create_collection_if_not_exists,
            reset_collection,
            clear_collection
        )

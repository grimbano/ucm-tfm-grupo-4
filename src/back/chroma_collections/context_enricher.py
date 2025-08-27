

from collections import defaultdict
from typing import Any, Callable, Iterable, List, Literal, Optional, Tuple, Union

import chromadb
from chromadb.api.collection_configuration import CreateCollectionConfiguration

from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings

from src.utils.customs import ChunkKey
from .base import ExtendedChromaCollection


class ContextEnricherChromaCollection(ExtendedChromaCollection):
    """
    A specialized ChromaDB collection for context-enriched search.

    This class extends `ExtendedChromaCollection` to provide advanced search
    functionality that not only retrieves relevant documents but also expands
    the context around them by including neighboring document chunks. This
    is particularly useful for RAG (Retrieval-Augmented Generation) applications
    where a broader context is needed to provide comprehensive answers.
    """


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
        Initializes the ContextEnricherChromaCollection.

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


    def enriched_context_search(
        self,
        queries: Union[str, List[str]],
        context_window_size: int,
        merge_results: bool = False,
        search_type: Literal['similarity', 'similarity_score_threshold', 'mmr'] = 'mmr',
        **kwargs: Any
    ) -> Union[List[str], List[List[str]]]:
        """
        Performs an enriched context search by retrieving relevant documents
        and their surrounding chunks.

        This method first performs a standard search to find the most relevant
        documents. It then uses the metadata of these documents to identify
        the full context they belong to (e.g., a full document or section).
        Finally, it retrieves a "window" of chunks around the relevant ones,
        merges them, and returns the enriched context.

        Args:
            queries: A single query string or a list of query strings.
            context_window_size: The desired number of chunks to include
                    in the context window around each relevant chunk.
            merge_results: If True, merges results from all queries into a single
                    list of unique documents.
            search_type: The type of search to perform. Options are 'similarity',
                    'similarity_score_threshold', or 'mmr'.
            **kwargs: Additional keyword arguments to pass to the underlying search method.

        Returns:
            A list of strings, where each string is the merged, enriched context
            for a query. If `merge_results` is False, returns a list of lists of
            strings, where each inner list corresponds to a query.
        """
        is_single_query = isinstance(queries, str)
        search_results = self.search(queries, search_type, **kwargs)

        if not search_results:
            return []
        
        if is_single_query:
            search_results = [search_results]
        
        if search_type == 'similarity_score_threshold':
            search_results = [
                [doc for doc, _ in query_result]
                for query_result in search_results
            ]

        if merge_results and not is_single_query:
            search_results = [self._merge_multiquery_search_results(search_results)]
        
        processed_results_dict = defaultdict(lambda: {
            ChunkKey.MIN_ID.value: float('inf'),
            ChunkKey.MAX_ID.value: float('-inf'),
            ChunkKey.TOTAL_CHUNKS.value: None
        })

        multi_query_output = []
        for query_results in search_results:
            for document in query_results:
                metadata_key = self._get_metadata_key_value_sorted(document.metadata)
                chunk_id = document.metadata.get(ChunkKey.HEADERS_CHUNK_ID.value)
                total_chunks = document.metadata.get(ChunkKey.HEADERS_CHUNKS_TOTAL.value)

                if chunk_id is not None and total_chunks is not None:
                    processed_results_dict[metadata_key][ChunkKey.MIN_ID.value] = min(
                        processed_results_dict[metadata_key][ChunkKey.MIN_ID.value],
                        chunk_id
                    )
                    processed_results_dict[metadata_key][ChunkKey.MAX_ID.value] = max(
                        processed_results_dict[metadata_key][ChunkKey.MAX_ID.value],
                        chunk_id
                    )
                    processed_results_dict[metadata_key][ChunkKey.TOTAL_CHUNKS.value] = total_chunks

            output_enriched_chunks = []
            for metadata_tuple, chunk_data in processed_results_dict.items():
                min_limit, max_limit = self._get_chunk_limits(
                    chunk_data[ChunkKey.MIN_ID.value],
                    chunk_data[ChunkKey.MAX_ID.value],
                    chunk_data[ChunkKey.TOTAL_CHUNKS.value],
                    window_size= context_window_size
                )

                conditions = [{k: {'$eq': v}} for k, v in metadata_tuple]
                conditions.append({ChunkKey.HEADERS_CHUNK_ID.value: {"$gte": min_limit}})
                conditions.append({ChunkKey.HEADERS_CHUNK_ID.value: {"$lte": max_limit}})

                window_results = self.get(
                    where= {"$and": conditions}
                )

                output_enriched_chunks.append(self._merge_overlap_chunks(window_results))
        
            multi_query_output.append(output_enriched_chunks)

        return (
            multi_query_output[0]
            if is_single_query or merge_results else
            multi_query_output
        )


    def _get_metadata_key_value_sorted(
            self,
            metadata: dict,
            exclude_keys: Optional[Iterable] = ChunkKey.EXTRA_CHUNKS_METADATA.value
    ) -> Tuple[Tuple[str, Any]]:
        """Sorts and filters a metadata dictionary for consistent comparison.

        This utility function creates a canonical representation of a metadata
        dictionary by sorting its key-value pairs. It's intended for use as a
        dictionary key to group similar documents.

        Args:
            metadata: The dictionary of metadata to process.
            exclude_keys: A collection of keys to exclude from the final
                    sorted output.

        Returns:
            A sorted tuple of (key, value) pairs, excluding the specified keys.
        """
        if not exclude_keys:
            exclude_keys = []
        
        return tuple(sorted((k, v) for k, v in metadata.items() if k not in exclude_keys))


    def _get_chunk_limits(
            self,
            md_min: int,
            md_max: int,
            md_total: int,
            window_size: int
    ) -> Tuple[int, int]:
        """Determines the start and end chunk indices for a given context window.

        This function calculates the valid start (inclusive) and end (inclusive)
        indices for a context window of size `window_size` based on a document's
        position (`md_min` and `md_max`) and the total number of documents.
        It handles edge cases for the beginning and end of the document set.

        Args:
            md_min: The starting index of the document.
            md_max: The ending index of the document.
            md_total: The total number of documents (0-indexed).
            window_size: The desired size of the context window.

        Returns:
            A tuple containing the start and end chunk indices (inclusive) for
            the context window.
        """
        chunk_count = md_max - md_min + 1
        if chunk_count >= window_size:
            return (md_min, md_max)

        remaining_needed = window_size - chunk_count
        add_before = remaining_needed // 2
        add_after = remaining_needed - add_before
        
        start_limit = md_min - add_before
        end_limit = md_max + add_after
        
        if start_limit < 0:
            end_limit += abs(start_limit)
            start_limit = 0
        
        if end_limit > md_total:
            start_limit -= (end_limit - md_total)
            end_limit = md_total
            if start_limit < 0:
                start_limit = 0
                
        return (start_limit, end_limit)


    def _find_overlap(self, chunk1: str, chunk2: str, max_overlap: int) -> int:
            """
            Finds the length of the longest overlap between the end of chunk1 and the start of chunk2.

            Args:
                chunk1: The first string.
                chunk2: The second string.
                max_overlap: The maximum allowed overlap length.

            Returns:
                The length of the longest overlap.
            """
            for i in range(min(len(chunk1), max_overlap), 0, -1):
                if chunk1.endswith(chunk2[:i]):
                    return i
            return 0


    def _merge_overlap_chunks(self, docs: dict) -> str:
        """Merges a list of overlapping document chunks into a single string.

        This function takes a dictionary of document metadata and content,
        sorts the chunks by their `headers_chunk_id`, and then concatenates
        them while removing the overlapping parts by dynamically finding
        the overlap size.

        Args:
            docs: A dictionary containing 'metadatas' and 'documents' from
                    a ChromaDB query.

        Returns:
            The final, merged string of all document chunks with overlaps removed.
        """

        if not docs.get('documents'):
            return ''

        chunks_data = []
        for metadata, content in zip(docs['metadatas'], docs['documents']):
            chunks_data.append(Document(metadata=metadata, page_content=content))

        sorted_chunks = sorted(chunks_data, key=lambda doc: doc.metadata.get(ChunkKey.HEADERS_CHUNK_ID.value, 0))

        first_chunk = sorted_chunks[0]
        reconstructed_parts = [first_chunk.page_content]
        max_overlap_size = first_chunk.metadata.get(ChunkKey.CHUNK_OVERLAP.value, 0)
        
        for i in range(1, len(sorted_chunks)):
            prev_chunk_content = sorted_chunks[i-1].page_content
            current_chunk_content = sorted_chunks[i].page_content
            
            overlap_size = self._find_overlap(prev_chunk_content, current_chunk_content, max_overlap_size)
            
            reconstructed_parts.append(current_chunk_content[overlap_size:])
            
        return "".join(reconstructed_parts)


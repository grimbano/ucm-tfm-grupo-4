

from collections import defaultdict
from copy import deepcopy
from email import header
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

import chromadb
from chromadb.api.types import IDs, Where, WhereDocument
from chromadb.api.collection_configuration import CreateCollectionConfiguration

from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings
from langchain_chroma import Chroma
import numpy as np

from src.utils.customs import DocumentWithScore, MdlKey


class ExtendedChromaCollection:
    """An extended and opinionated wrapper for the Langchain Chroma vector store.

    This class provides a robust interface for managing a single Chroma collection. 
    It offers enhanced initialization logic and streamlined methods for common 
    document management tasks, such as adding, deleting, and upserting data. 
    It also includes built-in validation to prevent common configuration errors, 
    making it safer and easier to use in production environments.
    """

    @staticmethod
    def cosine_distance_relevance_score_fn(distance: float) -> float:
        """Normalizes the cosine distance to a relevance score.

        The cosine distance, which ranges from [0, 2], is converted to a
        relevance score on a scale from [0, 1]. A distance of 0 (identical)
        results in a score of 1.0, representing maximum relevance, and a
        distance of 2 (opposite) results in a score of 0.0, representing
        no relevance.

        Args:
            distance: The cosine distance between two vectors, ranging from 0.0 to 2.0.

        Returns:
            A normalized relevance score from 0.0 to 1.0.
        """
        return 1.0 - distance / 2


    @staticmethod
    def convert_to_json_serializable(
        documents: List[Union[Document, DocumentWithScore]],
        return_fields: Optional[List[Literal['id', 'page_content', 'metadata', 'score']]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Converts a list of documents or document-score tuples into a JSON-serializable format.

        This method processes a list that can contain either `Document` objects or `DocumentWithScore`
        tuples. It allows for the selective inclusion of document attributes in the output
        dictionaries based on the `return_fields` parameter.

        Args:
            documents: A list containing either `Document` objects or `DocumentWithScore` tuples.
                    The list should contain only one type of object.
            return_fields: An optional list of strings specifying which fields to include
                    in the output dictionaries. If None, all available fields ('id',
                    'page_content', 'metadata', 'score') are returned.

        Returns:
            A list of dictionaries, where each dictionary represents a document with the
            requested fields. Fields with falsy values (e.g., None, empty string) are
            excluded from the output.
        
        Raises:
            TypeError: If the input list contains a mix of `Document` objects and
                    `DocumentWithScore` tuples.
        """
        if not documents:
            return []
        
        if not return_fields:
            return_fields = ['id', 'page_content', 'metadata', 'score']
        
        is_document_list = isinstance(documents[0], Document)

        json_list = []
        for item in documents:
            doc_dict = {}
            doc = None
            score = None

            if is_document_list:
                doc = item
            else:
                doc, score = item

            if doc.id and 'id' in return_fields:
                doc_dict['id'] = doc.id

            if doc.page_content and 'page_content' in return_fields:
                doc_dict['page_content'] = doc.page_content

            if doc.metadata and 'metadata' in return_fields:
                doc_dict['metadata'] = doc.metadata

            if score and 'score' in return_fields:
                doc_dict['score'] = score
            
            if doc_dict:
                json_list.append(doc_dict)

        return json_list


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
        """Initializes an ExtendedChromaCollection instance.

        This constructor provides a flexible and opinionated interface to manage a
        Chroma vector store. It handles common setup tasks like creating, resetting,
        or clearing a collection based on the provided arguments.

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
        is_persistent_client = persist_directory or host or chroma_cloud_api_key

        if reset_collection and clear_collection:
            raise ValueError("Cannot set both 'reset_collection' and 'clear_collection' to True.")
        
        if is_persistent_client and create_collection_if_not_exists:
            if reset_collection or clear_collection:
                raise ValueError("Cannot 'reset_collection' or 'clear_collection' if a persistent collection (local or remote) needs to be created.")

        if not create_collection_if_not_exists and collection_configuration:
            raise ValueError("'collection_configuration' must be None if 'create_collection_if_not_exists' is False.")

        self._collection_name = collection_name
        self._embedding_function = embedding_function
        self._persist_directory = persist_directory
        self._host = host
        self._port = port
        self._ssl = ssl
        self._headers = headers
        self._chroma_cloud_api_key = chroma_cloud_api_key
        self._tenant = tenant or 'default_tenant'
        self._database = database or 'default_database'
        self._client = client
        self._relevance_score_fn = relevance_score_fn if relevance_score_fn else self.cosine_distance_relevance_score_fn

        if not is_persistent_client and self._client is None:
            self._client = chromadb.Client(
                settings=chromadb.config.Settings(is_persistent=False)
            )
        
        if reset_collection:
            if not self._reset_collection():
                raise RuntimeError(f"It was not possible to delete '{self._collection_name}'")

        self._chroma_vectorstore = Chroma(
            collection_name= self._collection_name,
            embedding_function= self._embedding_function,
            persist_directory= self._persist_directory,
            host= self._host,
            port= self._port,
            ssl= self._ssl,
            headers= self._headers,
            chroma_cloud_api_key= self._chroma_cloud_api_key,
            tenant= self._tenant,
            database= self._database,
            client_settings= client_settings,
            collection_metadata= collection_metadata,
            collection_configuration= collection_configuration,
            client= self._client,
            relevance_score_fn= self._relevance_score_fn,
            create_collection_if_not_exists= create_collection_if_not_exists
        )

        if clear_collection:
            self._cleared_docs = self.delete_documents()


    def get(
        self,
        ids: Optional[Union[str, List[str]]] = None,
        where: Optional[Where] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        where_document: Optional[WhereDocument] = None,
        include: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves documents and their associated metadata from the vector store.

        This method acts as a wrapper for the underlying vector store's get operation.
        It allows for fetching documents by their unique identifiers (IDs) or by
        filtering based on metadata and document content. The returned data includes
        the document content, metadata, and embeddings, depending on the `include`
        parameter.

        Args:
            ids: A single ID or a list of IDs of the documents to retrieve. If not
                    provided, the query will be filtered by `where` and `where_document`.
            where: A dictionary-like object specifying a filter for document metadata.
                    Only documents where the metadata matches the filter will be
                    retrieved.
            limit: The maximum number of documents to retrieve. Defaults to no limit.
            offset: The number of documents to skip from the beginning of the results.
                    Useful for pagination.
            where_document: A dictionary-like object specifying a filter for the
                    document content.
            include: A list of strings to specify which data to include in the
                    response. Options typically include 'metadatas', 'documents',
                    and 'embeddings'.

        Returns:
            A dictionary containing the retrieved documents and their associated data.
            The exact structure of the dictionary depends on the `include` parameter.

        Raises:
            Any exceptions raised by the underlying `_chroma_vectorstore.get` method.
        """
        return self._chroma_vectorstore.get(
            ids= ids,
            where= where,
            limit= limit,
            offset= offset,
            where_document= where_document,
            include= include
        )


    def search(
        self,
        queries: Union[str, List[str]],
        search_type: Literal['similarity', 'similarity_score_threshold', 'mmr'],
        merge_results: bool = False,
        **kwargs: Any
    ) -> Union[List[Document], List[DocumentWithScore], List[List[Document]], List[List[DocumentWithScore]]]:
        """Performs a search on the vector store using one or more queries.

        This method serves as a flexible wrapper around the various search functionalities
        provided by the underlying Chroma vector store. It can handle a single query or a
        list of queries and adapts the search call based on the specified `search_type`.
        All additional keyword arguments are passed directly to the appropriate search method,
        allowing for fine-grained control over parameters like `k`, `filter`, and `score_threshold`.

        Args:
            queries: A single query string or a list of query strings.
            search_type: The type of search to perform. Must be one of 'similarity',
                    'similarity_score_threshold', or 'mmr'.
            merge_results: If True, merges results from all queries into a single
                    list of unique documents.
            **kwargs: Arbitrary keyword arguments to pass to the underlying search method,
                    such as `k` (number of results), `filter`, or `score_threshold`.

        Returns:
            A list of search results.
            - If `queries` is a single string (`str`), it returns a single list of results.
            The format of this list depends on the `search_type`:
            - 'similarity' or 'mmr': A list of `Document` objects.
            - 'similarity_score_threshold': A list of tuples `(Document, score)`.
            - If `queries` is a list of strings (`List[str]`), it returns a list of lists,
            where each inner list corresponds to a query and its format matches the
            descriptions above.

        Raises:
            ValueError: If an unsupported `search_type` is provided.
        """
        is_single_query = isinstance(queries, str)

        _queries = [queries] if is_single_query else queries

        if search_type == "similarity":
            results = [
                self._chroma_vectorstore.similarity_search(query, **kwargs)
                for query in _queries
            ]
        
        elif search_type == "similarity_score_threshold":
            results = [
                self._chroma_vectorstore.similarity_search_with_relevance_scores(query, **kwargs)
                for query in _queries
            ]
        
        elif search_type == "mmr":
            results = [
                self._chroma_vectorstore.max_marginal_relevance_search(query, **kwargs)
                for query in _queries
            ]
        
        else:
            msg = (
                f"search_type of {search_type} not allowed. Expected "
                "search_type to be 'similarity', 'similarity_score_threshold'"
                " or 'mmr'."
            )
            raise ValueError(msg)
        
        return results[0] if is_single_query else results


    def delete_documents(
        self,
        ids: Optional[Union[str, List[str]]] = None,
        where: Optional[Where] = None,
        where_document: Optional[WhereDocument] = None,
        include: Optional[List[str]] = ['documents', 'metadatas']
    ) -> Dict[str, Any]:
        """
        Deletes documents from the collection based on IDs or metadata.

        Args:
            ids: The ID(s) of the documents to delete.
            where: A query to filter documents by metadata.
            where_document: A query to filter documents by content.
            include: List of fields to include in the returned deleted
                    documents dictionary.

        Returns:
            A dictionary containing the deleted document IDs, documents, and
            metadatas, based on the `include` parameter.
        """
        retrieved_docs = self.get(
            ids= ids,
            where= where,
            where_document= where_document,
            include= include
        )

        if retrieved_docs.get('ids', None):
            self._chroma_vectorstore.delete(
                ids= retrieved_docs.get('ids', None),
                where= where,
                where_document= where_document
            )

        return {k: v for k, v in retrieved_docs.items() if k in ['ids'] + include}
    
    
    def delete_by_file_name(self, file_names: Union[str, List[str]]) -> Dict[str, Any]:
        """
        Deletes documents from the collection based on their file names.

        Args:
            file_names: A single file name or a list of file names to delete.

        Returns:
            A dictionary containing the deleted document IDs, documents, and metadatas.
        """
        _file_names = [file_names] if isinstance(file_names, str) else file_names
        return self.delete_documents(where= {MdlKey.FILE_NAME.value: {'$in': _file_names}})


    def add_documents(self, documents: List[Document], **kwargs: Any) -> IDs:
        """
        Adds a list of documents to the underlying vector store.

        This method serves as a flexible wrapper, allowing you to pass any
        additional keyword arguments directly to the vector store's
        `add_documents` method. This is particularly useful for passing
        parameters like `ids` or `metadatas` if the underlying vector store
        supports them.

        Args:
            documents: A list of `Document` objects to be added.
            **kwargs: Additional keyword arguments to be passed to the vector store.

        Returns:
            The result of the underlying vector store's `add_documents` method,
            which typically includes the IDs of the newly added documents.
        """
        return self._chroma_vectorstore.add_documents(documents, **kwargs)
    

    def upsert_documents(self, documents: List[Document]) -> Tuple[Dict[str, Any], IDs]:
        """
        Deletes existing documents by file name and adds new ones.

        This method first identifies the file names from the provided documents,
        deletes all documents associated with those file names, and then adds
        the new documents.

        Args:
            documents: The list of documents to upsert.

        Returns:
            A tuple containing a dictionary of deleted documents and a list of
            IDs for the newly added documents.
        """
        file_names = {
            doc.metadata.get(MdlKey.FILE_NAME.value) 
            for doc in documents 
            if doc.metadata.get(MdlKey.FILE_NAME.value) 
        }

        deleted_docs = self.delete_by_file_name(file_names= list(file_names))
        added_ids = self.add_documents(documents)

        return (deleted_docs, added_ids)


    def upsert_documents(self, documents: List[Document]) -> Tuple[Dict[str, Any], IDs]:
        """
        Deletes existing documents by file name and adds new ones.

        This method first identifies the file names from the provided documents,
        deletes all documents associated with those file names, and then adds
        the new documents.

        Args:
            documents: The list of documents to upsert.

        Returns:
            A tuple containing a dictionary of deleted documents and a list of 
            IDs for the newly added documents.
        """
        file_names = {
            doc.metadata.get(MdlKey.FILE_NAME.value) 
            for doc in documents 
            if doc.metadata.get(MdlKey.FILE_NAME.value) 
        }

        deleted_docs = self.delete_by_file_name(file_names= list(file_names))
        added_ids = self.add_documents(documents)

        return (deleted_docs, added_ids)


    def _reset_collection(self) -> bool:
        """
        Deletes the underlying Chroma collection.

        Returns:
            True if the collection was successfully deleted, False otherwise.
        """
        try:
            temp_chroma_vectorstore = Chroma(
                persist_directory= self._persist_directory,
                collection_name= self._collection_name
            )

            temp_chroma_vectorstore.delete_collection()
            return True
        
        except:
            return False


    def _merge_multiquery_search_results(
        self,
        multi_query_results: List[List[Union[Document, DocumentWithScore]]],
    ) -> List[Document]:
        """
        Merges and deduplicates search results from multiple queries.

        This method intelligently handles two types of search results:
        1. A list of `Document` objects: It flattens the list and removes duplicates
            based on the unique document ID, preserving the order of the first occurrence.
        2. A list of `DocumentWithScore` tuples: It flattens the list and aggregates
            results for the same document ID, calculating the **average score** for
            each unique document.

        Args:
            multi_query_results: A nested list where each inner list represents the
                    search results for a single query. The inner lists can contain 
                    either `Document` objects or `DocumentWithScore` tuples, but not a mix.

        Returns:
            A single, flattened list of unique search results. If the input contained
            scores, the output will be a list of `DocumentWithScore` tuples with
            averaged scores.
        """
        first_non_empty_list = next((lst for lst in multi_query_results if lst), None)

        if not first_non_empty_list:
            return []

        if isinstance(first_non_empty_list[0], Document):
            return self._merge_unique_documents(multi_query_results)
        else:
            return self._merge_and_average_scores(multi_query_results)


    def _merge_unique_documents(self, multi_query_results: List[List[Document]]) -> List[Document]:
        """
        Merges a list of Document lists into a single list of unique documents.

        This method flattens a nested list of `Document` objects and removes duplicates
        based on their unique IDs. It maintains the order of the documents as they
        first appeared.

        Args:
            multi_query_results: A list of lists of `Document` objects.

        Returns:
            A flattened list containing only unique `Document` objects.
        """
        processed_docs = set()
        unique_documents = []

        for query_results in multi_query_results:
            for doc in query_results:
                if doc.id not in processed_docs:
                    unique_documents.append(doc)
                    processed_docs.add(doc.id)

        return unique_documents


    def _merge_and_average_scores(
        self,
        multi_query_results: List[List[DocumentWithScore]]
    ) -> List[DocumentWithScore]:
        """
        Merges and averages scores for duplicate documents in a list of results.

        This method processes a nested list of `DocumentWithScore` tuples. For each
        unique document, it sums the scores from all its occurrences and calculates
        the average. The final list contains one `DocumentWithScore` tuple per
        unique document, with the averaged score.

        Args:
            multi_query_results: A list of lists of `DocumentWithScore` tuples.

        Returns:
            A flattened list of `DocumentWithScore` tuples, with duplicate documents
            removed and their scores averaged.
        """
        doc_scores = defaultdict(lambda: {'document': None, 'scores': []})
        
        for query_results in multi_query_results:
            for doc, score in query_results:
                doc_scores[doc.id]['scores'].append(score)
                if doc_scores[doc.id]['document'] is None:
                    doc_scores[doc.id]['document'] = doc

        return [
            DocumentWithScore(doc_data['document'], np.mean(doc_data['scores']))
            for _, doc_data in doc_scores.items()
        ]


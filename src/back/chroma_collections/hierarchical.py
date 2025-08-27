
from copy import deepcopy
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import chromadb
from chromadb.api.types import IDs
from chromadb.api.collection_configuration import CreateCollectionConfiguration

from langchain_core.documents import Document
from langchain.embeddings.base import Embeddings

import numpy as np

from src.utils.customs import HierarchicalKey, MdlKey
from .base import ExtendedChromaCollection


class MdlHierarchicalChromaCollections:
    """Manages a set of interconnected Chroma collections with a hierarchical structure.

    This class provides a unified and robust interface for managing multiple
    vector stores that have a parent-child relationship, such as tables and their
    corresponding columns. It streamlines complex operations like hierarchical search,
    adding, and deleting documents across multiple collections, ensuring data
    consistency and integrity.

    By encapsulating the management of both the parent (e.g., table summaries) and
    child (e.g., column details) collections, this class simplifies common workflows
    and guarantees that related data is handled cohesively.
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
        return ExtendedChromaCollection.cosine_distance_relevance_score_fn(distance)


    def __init__(
        self,

        collection_names: Tuple[str, str],
        embedding_function: Optional[Embeddings] = None,
        persist_directory: Optional[str] = None,
        host: Optional[str] = None,
        port: Optional[int] = None,
        ssl: bool = False,
        headers: Optional[dict[str, str]] = None,
        chroma_cloud_api_key: Optional[str] = None,
        tenant: Optional[str] = None,
        database: Optional[str] = None,
        collections_configuration: Optional[CreateCollectionConfiguration] = None,
        relevance_score_fn: Optional[Callable[[float], float]] = None,
        create_collections_if_not_exists: bool = True,
        reset_collections: Optional[bool] = False,
        clear_collections: Optional[bool] = False,
    ):
        """
        Initializes the MdlHierarchicalChromaCollections.

        Args:
            collection_names: A tuple containing the names of the collections to manage 
                    (e.g., ('tables', 'columns')).
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
            collections_configuration: An optional configuration object to pass when
                    creating the collections. This is ignored if `create_collections_if_not_exists` is False.
            relevance_score_fn: A function to transform raw relevance scores (e.g., cosine similarity)
                    into a desired scale.Defaults to `cosine_distance_relevance_score_fn`.
            create_collections_if_not_exists: If True, creates the collections if they don't
                    exist. Otherwise, it will attempt to connect to existing collections.
            reset_collection: If True, the existing collection will be deleted and a new one will 
                    be created upon initialization. This cannot be used with `clear_collection`.
            clear_collection: If True, all documents within the collection will be deleted upon
                    initialization, but the collection itself will persist.
                    This cannot be used with `reset_collection`.
        """
        self._collection_names = collection_names
        self._embedding_function = embedding_function
        self._persist_directory = persist_directory
        self._host = host
        self._port = port
        self._ssl = ssl
        self._headers = headers
        self._chroma_cloud_api_key = chroma_cloud_api_key
        self._tenant = tenant or 'default_tenant'
        self._database = database or 'default_database'
        self._tables_collection_name = self._collection_names[0]
        self._columns_collection_name = self._collection_names[1]
        self._relevance_score_fn = relevance_score_fn or self.cosine_distance_relevance_score_fn
        self._collections: Dict[str, ExtendedChromaCollection] = {}

        for collection_name in self._collection_names:
            self._collections[collection_name] = ExtendedChromaCollection(
                collection_name= collection_name,
                embedding_function= self._embedding_function,
                persist_directory= self._persist_directory,
                host= self._host,
                port= self._port,
                ssl= self._ssl,
                headers= self._headers,
                chroma_cloud_api_key= self._chroma_cloud_api_key,
                tenant= self._tenant,
                database= self._database,
                collection_configuration= collections_configuration,
                relevance_score_fn= self._relevance_score_fn,
                create_collection_if_not_exists= create_collections_if_not_exists,
                reset_collection= reset_collections,
                clear_collection= clear_collections
            )
    

    def delete_by_file_name(self, file_name: str) -> Tuple[Dict[str, Any]]:
        """
        Deletes documents by file name across all managed collections.

        Args:
            file_name: The name of the file whose documents should be deleted.

        Returns:
            A tuple of dictionaries, where each dictionary contains the deleted
            document information for each collection.
        """
        deleted_docs = [
            self._collections[name].delete_by_file_name(file_names= file_name)
            for name in self._collection_names
        ]

        return tuple(deleted_docs)


    def add_documents(self, documents: Tuple[List[Document]]) -> Tuple[IDs]:
        """
        Adds a collection of documents to the vector store.

        This method is a wrapper around the underlying vector store's `add_documents`
        method, designed to handle two distinct sets of documents: one for tables
        and another for columns. It ensures that the documents are added to their
        respective collections.

        Args:
            documents: A tuple containing two lists of `Document` objects.
                    The first list is for table documents, and the second is for column documents.

        Returns:
            A tuple containing two lists of IDs, corresponding to the added tables
            and columns, respectively.
        """
        tables_documents, columns_documents = documents

        tables_collection = self._collections[self._tables_collection_name]
        columns_collection = self._collections[self._columns_collection_name]

        added_tables_ids = tables_collection.add_documents(tables_documents)
        added_columns_ids = columns_collection.add_documents(columns_documents)

        return (added_tables_ids, added_columns_ids)
    

    def upsert_hierarchical_data(self, documents: Tuple[List[Document]]) -> Tuple[Tuple[Dict[str, Any], IDs]]:
        """
        Upserts hierarchical data (tables and columns) into the collections.

        This method deletes all documents associated with the file names of the
        provided tables, then adds the new tables and columns.

        Args:
            documents (Tuple[List[Document], List[Document]]): A tuple containing
                    a list of table documents and a list of column documents.

        Returns:
            Tuple[Tuple[Dict[str, Any], ...], Tuple[IDs, IDs]]: A tuple containing a tuple
                    of deleted document dictionaries and a tuple of new IDs.
        """
        tables_documents, _ = documents

        file_names = list({
            doc.metadata.get(MdlKey.FILE_NAME.value) 
            for doc in tables_documents
            if doc.metadata.get(MdlKey.FILE_NAME.value) 
        })

        deleted_docs = self.delete_by_file_name(file_names= file_names)
        added_ids = self.add_documents(documents)

        return (deleted_docs, added_ids)
    

    def hierarchical_similarity_search(
        self,
        queries: Union[str, List[str]],
        k_tables: int = 10,
        tables_score_threshold: float = 0.75,
        k_columns: int = 10,
        columns_score_threshold: float = 0.75,
        merge_results: bool = True
    ) -> Union[List[Dict[str, Any]], List[List[Dict[str, Any]]]]:
        """
        Performs a hierarchical similarity search with multiple queries.

        This method searches for relevant tables based on the provided queries. For each 
        retrieved table, it then performs a filtered search for relevant columns.
        Relevance scores from multiple queries are used for filtering and consolidation.
        
        The final results are sorted hierarchically: tables are ordered by their 
        relevance score in descending order, and the columns within each table 
        are also sorted by their relevance score in descending order.

        Args:
            queries: A single query string or a list of query strings to search for.
            k_tables: The number of top tables to retrieve per query.
            tables_score_threshold: The minimum relevance score for a table to be included
                    in the search results.
            k_columns: The number of top columns to retrieve per query, filtered by their
                    associated table.
            columns_score_threshold: The minimum relevance score for a column to be included
                    in the search results.
            merge_results: A boolean flag. If True, the results from all queries are merged
                    into a single list of unique tables. If False, a list of results is returned,
                    where each member corresponds to a single query and contains its specific results.

        Returns:
            - If `merge_results` is True, returns a list of dictionaries, where each
                dictionary represents a unique table with its content, average relevance
                score, and a list of its unique, relevant columns.
            - If `merge_results` is False, returns a list of lists of dictionaries.
                Each inner list corresponds to a query and contains its individual results.
        """
        is_single_query = isinstance(queries, str)
        _queries = [queries] if is_single_query else queries

        tables_collection = self._collections[self._tables_collection_name]
        columns_collection = self._collections[self._columns_collection_name]

        multi_query_results = []

        for query in _queries:
            tables_results = tables_collection.search(
                queries= query,
                search_type= 'similarity_score_threshold',
                k= k_tables,
                score_threshold= tables_score_threshold
            )

            query_result = []
            for table_doc, table_score in tables_results:
                table_id = table_doc.id

                columns_results = columns_collection.search(
                    queries= query,
                    search_type= 'similarity_score_threshold',
                    filter= {MdlKey.TABLE_ID.value: table_id},
                    k= k_columns,
                    score_threshold= columns_score_threshold
                )

                if columns_results:
                    query_result.append({
                        HierarchicalKey.TABLE_SUMMARY.value: {
                            HierarchicalKey.ID.value: table_id,
                            HierarchicalKey.CONTENT.value: table_doc.page_content,
                            HierarchicalKey.RELEVANCE_SCORE.value: table_score
                        },
                        HierarchicalKey.COLUMNS.value: [
                            {
                                HierarchicalKey.ID.value: column_doc.id,
                                HierarchicalKey.CONTENT.value: column_doc.page_content,
                                HierarchicalKey.RELEVANCE_SCORE.value: column_score
                            } 
                            for column_doc, column_score in columns_results
                        ]
                    })
            
            multi_query_results.append(query_result)
            
        return (
            self._merge_search_results(multi_query_results)
            if not is_single_query and merge_results else
            self._remove_ids(multi_query_results)
        )


    def _remove_ids(
        self,
        results: Union[List[Dict[str, Any]], List[List[Dict[str, Any]]]]
    ) -> Union[List[Dict[str, Any]], List[List[Dict[str, Any]]]]:
        """
        Removes the 'id' field from the search results.

        This method processes a list of search results, which can be either a single 
        query's results or multiple queries' results, and returns a new structure 
        with the 'id' key removed from all dictionaries. The original sorting and 
        hierarchical structure are preserved.

        Args:
            results: A list of search results. Can be a list of table dictionaries
                    (for a single query) or a list of lists of table dictionaries 
                    (for multiple queries).

        Returns:
            A new list of results with the 'id' key removed. The type of the return 
            value matches the type of the input list.
        """
        if not results:
            return results
        
        is_single_query = (isinstance(results[0], list) and len(results) == 1)
        _results = results

        if isinstance(results[0], dict):
            _results = [results]
            is_single_query = True

        updated_results = [
            [
                {
                    HierarchicalKey.TABLE_SUMMARY.value: {
                        HierarchicalKey.CONTENT.value: table_data[HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.CONTENT.value],
                        HierarchicalKey.RELEVANCE_SCORE.value: table_data[HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.RELEVANCE_SCORE.value]
                    },
                    HierarchicalKey.COLUMNS.value: [
                        {
                            HierarchicalKey.CONTENT.value: column_data[HierarchicalKey.CONTENT.value],
                            HierarchicalKey.RELEVANCE_SCORE.value: column_data[HierarchicalKey.RELEVANCE_SCORE.value]
                        }
                        for column_data in table_data[HierarchicalKey.COLUMNS.value]
                    ]
                }
                for table_data in query_result
            ]
            for query_result in _results
        ]

        return updated_results[0] if is_single_query else updated_results


    def _merge_search_results(
        self,
        multi_query_results: List[List[Dict[str, Any]]]
    ) -> List[Dict[str, Any]]:
        """
        Merges and consolidates search results from multiple queries.
        
        Args:
            multi_query_results: A list of lists, where each inner list contains
                the results for a single query.
        
        Returns:
            A single list of consolidated dictionaries, sorted by relevance score.
        """
        merged_results_dict = defaultdict(lambda: {HierarchicalKey.TABLE_SUMMARY.value: None, HierarchicalKey.COLUMNS.value: {}})

        _multi_query_results = deepcopy(multi_query_results)

        for query_result in _multi_query_results:
            for table_data in query_result:
                table_id = table_data[HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.ID.value]
                table_content = table_data[HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.CONTENT.value]
                table_score = table_data[HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.RELEVANCE_SCORE.value]
                columns = table_data[HierarchicalKey.COLUMNS.value]

                if table_id not in merged_results_dict:
                    merged_results_dict[table_id][HierarchicalKey.TABLE_SUMMARY.value] = {
                        HierarchicalKey.CONTENT.value: table_content,
                        HierarchicalKey.RELEVANCE_SCORE.value: [table_score]
                    }

                    merged_results_dict[table_id][HierarchicalKey.COLUMNS.value] = {
                        column_data[HierarchicalKey.ID.value]: {
                            HierarchicalKey.CONTENT.value: column_data[HierarchicalKey.CONTENT.value],
                            HierarchicalKey.RELEVANCE_SCORE.value: [column_data[HierarchicalKey.RELEVANCE_SCORE.value]]
                        } for column_data in columns
                    }
                    continue

                merged_results_dict[table_id][HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.RELEVANCE_SCORE.value].append(table_score)

                for column_data in columns:
                    column_id = column_data[HierarchicalKey.ID.value]
                    column_content = column_data[HierarchicalKey.CONTENT.value]
                    column_score = column_data[HierarchicalKey.RELEVANCE_SCORE.value]

                    if column_id not in merged_results_dict[table_id][HierarchicalKey.COLUMNS.value]:
                        merged_results_dict[table_id][HierarchicalKey.COLUMNS.value][column_id] = {
                            HierarchicalKey.CONTENT.value: column_content,
                            HierarchicalKey.RELEVANCE_SCORE.value: [column_score]
                        }
                        continue

                    merged_results_dict[table_id][HierarchicalKey.COLUMNS.value][column_id][HierarchicalKey.RELEVANCE_SCORE.value].append(column_score)

        results = []
        for table_result in merged_results_dict.values():
            if not (table_result[HierarchicalKey.TABLE_SUMMARY.value] and table_result[HierarchicalKey.COLUMNS.value]):
                continue

            final_table_score = np.mean(table_result[HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.RELEVANCE_SCORE.value])
            
            columns = [
                {
                    HierarchicalKey.CONTENT.value: column_result[HierarchicalKey.CONTENT.value],
                    HierarchicalKey.RELEVANCE_SCORE.value: np.mean(column_result[HierarchicalKey.RELEVANCE_SCORE.value])
                }
                for column_result in table_result[HierarchicalKey.COLUMNS.value].values()
            ]
            
            sorted_columns = sorted(
                columns,
                key=lambda c: c[HierarchicalKey.RELEVANCE_SCORE.value],
                reverse=True
            )
            
            results.append({
                HierarchicalKey.TABLE_SUMMARY.value: {
                    HierarchicalKey.CONTENT.value: table_result[HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.CONTENT.value],
                    HierarchicalKey.RELEVANCE_SCORE.value: final_table_score
                },
                HierarchicalKey.COLUMNS.value: sorted_columns
            })


        return sorted(
            results, 
            key=lambda t: t[HierarchicalKey.TABLE_SUMMARY.value][HierarchicalKey.RELEVANCE_SCORE.value],
            reverse=True
        )




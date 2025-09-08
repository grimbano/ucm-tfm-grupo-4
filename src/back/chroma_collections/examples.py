

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


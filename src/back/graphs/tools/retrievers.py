

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional, Union
from pydantic import BaseModel
from langchain.tools import BaseTool, tool

from ...chroma_collections import (
    ContextEnricherChromaCollection,
    ExamplesChromaCollection,
    MdlHierarchicalChromaCollections
)
from ..pydantic_models import create_retriever_input_class


__NO_RELEVANT_RESULTS_MSG = 'No semantically relevant results were found for the specified queries.'


class BaseRetrieverTool(ABC):
    """
    Base class for creating retrieval tools with a dynamic factory pattern.

    This class provides a common structure for retriever tools by encapsulating
    the collection instance and dynamically creating a tool object from the
    subclass's `run` method. This allows tool name, description, and argument
    schema to be defined at runtime.
    """
    def __init__(
        self,
        collection_instance: Union[ContextEnricherChromaCollection, MdlHierarchicalChromaCollections, ExamplesChromaCollection],
        tool_name: str,
        max_subqueries: int,
        tool_description: Optional[str],
    ):
        """
        Initializes the base retriever tool.

        Args:
            collection_instance: The Chroma collection instance for retrieval.
            tool_name: The name of the tool.
            max_subqueries: The maximum number of subqueries the tool's input schema will accept.
            tool_description: A description for the tool, used by the agent.
        """
        self._collection = collection_instance
        self._tool_name = tool_name
        self._tool_description = tool_description

        if not isinstance(max_subqueries, int) or max_subqueries < 1:
            raise ValueError("'max_subqueries' must be an integer greater than or equal to 1.")
        self._max_subqueries = max_subqueries

        self.tool_instance: BaseTool = self._create_tool(tool_name, tool_description, max_subqueries)


    def _create_tool(
            self,
            tool_name: str,
            tool_description: str,
            max_subqueries: int
        ) -> BaseTool:
        """
        Dynamically creates the tool instance using the run method from the subclass.

        Returns:
            A dynamically created tool object.
        """
        self_ref = self
        args_schema = create_retriever_input_class(max_subqueries= max_subqueries)

        @tool(tool_name, description= tool_description, args_schema= args_schema)
        def tool_func(queries: List[str]) -> Union[List[str], List[Dict[str, str]]]:
            """This wrapper function calls the abstract `run` method of the subclass instance."""
            return self_ref.run(queries)
        
        return tool_func


    @abstractmethod
    def run(self, queries: List[str]) -> Union[List[str], List[Dict[str, str]]]:
        """
        Abstract method for the retrieval logic, to be implemented by subclasses.
        This method is called by the tool's wrapper function.
        """
        pass



class BusinessLogicRetrieverTool(BaseRetrieverTool):
    """
    A tool for retrieving business logic chunks from a Chroma collection.

    This class encapsulates the specific retrieval logic and parameters for
    business logic data. It leverages the `BaseRetrieverTool` to dynamically
    expose its `run` method as a callable tool.
    """
    def __init__(
        self,
        business_logic_collection: ContextEnricherChromaCollection,
        max_subqueries: Optional[int] = 5,
        context_window_size: Optional[int] = 3,
        k: Optional[int] = 10,
        fetch_k: Optional[int] = 25,
        lambda_mult: Optional[float] = 0.5
    ):
        """
        Initializes the business logic retriever with its specific parameters.

        Args:
            business_logic_collection: The collection instance for retrieving business logic.
            max_subqueries: The maximum number of subqueries the tool's input schema will accept.
            context_window_size: The number of chunks to include in the context window.
            k: The number of results to return.
            fetch_k: The number of results to fetch for MMR reranking.
            lambda_mult: The diversity control parameter for MMR.
        """
        self._context_window_size = context_window_size
        self._k = k
        self._fetch_k = fetch_k
        self._lambda_mult = lambda_mult
        
        tool_name = "business_logic_retriever"
        tool_description = (
            "Retrieve detailed business logic, including KPI calculations, "
            "domain-specific rules, and definitions of business concepts.\n"
            "This is the primary source for understanding the semantic meaning and 'why' behind the data.\n"
            "Provide multiple queries to cover all relevant business aspects."
        )

        super().__init__(
            collection_instance= business_logic_collection,
            tool_name= tool_name,
            tool_description= tool_description,
            max_subqueries= max_subqueries
        )


    def run(self, queries: List[str]) -> List[str]:
        """
        Implements the retrieval logic for this tool.

        Args:
            queries: A list of search queries.

        Returns:
            A list of strings with the retrieved results.
        """
        search_results = self._collection.enriched_context_search(
            search_type='mmr',
            merge_results=True,
            queries=queries,
            context_window_size=self._context_window_size,
            k=self._k,
            fetch_k=self._fetch_k,
            lambda_mult=self._lambda_mult,
        )

        return search_results if search_results else [__NO_RELEVANT_RESULTS_MSG]



class MdlRetrieverTool(BaseRetrieverTool):
    """
    A tool for retrieving MDL data.

    This tool provides table schemas, column definitions, and keys to
    aid in constructing valid SQL queries.
    """
    def __init__(
        self,
        mdl_collection: MdlHierarchicalChromaCollections,
        max_subqueries: Optional[int] = 5,
        k_tables: Optional[int] = 10,
        tables_score_threshold: Optional[float] = 0.75,
        k_columns: Optional[int] = 15,
        columns_score_threshold: Optional[float] = 0.75
    ):
        """
        Initializes the MDL retriever with its specific parameters.

        Args:
            mdl_collection: The collection instance for retrieving MDL data.
            max_subqueries: The maximum number of subqueries.
            k_tables: The number of top tables to retrieve.
            tables_score_threshold: The relevance score threshold for tables.
            k_columns: The number of top columns to retrieve.
            columns_score_threshold: The relevance score threshold for columns.
        """
        self._k_tables = k_tables
        self._tables_score_threshold = tables_score_threshold
        self._k_columns = k_columns
        self._columns_score_threshold = columns_score_threshold

        tool_name = "mdl_retriever"
        tool_description = (
            "Retrieve table schemas, column definitions, primary and foreign keys.\n"
            "This tool is essential for identifying the specific tables and columns required to construct a valid SQL query.\n"
            "It provides the 'what' and 'where' of the data."
        )

        super().__init__(
            collection_instance= mdl_collection,
            tool_name= tool_name,
            tool_description= tool_description,
            max_subqueries= max_subqueries
        )


    def run(self, queries: List[str]) -> List[Dict[str, str]]:
        """
        Implements the retrieval logic for MDL data.

        Args:
            queries: A list of search queries.

        Returns:
            A list of dictionaries with the retrieved results.
        """
        search_results = self._collection.hierarchical_similarity_search(
            merge_results=True,
            show_relevance_score=False,
            queries=queries,
            k_tables=self._k_tables,
            tables_score_threshold=self._tables_score_threshold,
            k_columns=self._k_columns,
            columns_score_threshold=self._columns_score_threshold
        )
        return search_results if search_results else [__NO_RELEVANT_RESULTS_MSG]



class ExamplesRetrieverTool(BaseRetrieverTool):
    """
    A tool for retrieving relevant examples from a collection.

    This tool is useful for finding specific instances, snippets, or precedents to
    inform the final answer, ensuring accuracy and consistency.
    """
    def __init__(
        self,
        examples_collection: ExamplesChromaCollection,
        k: Optional[int] = 2,
        max_subqueries: Optional[int] = 1,
    ):
        """
        Initializes the examples retriever with its specific parameters.

        Args:
            examples_collection: The collection instance for retrieving examples.
            k: The number of results to retrieve.
            max_subqueries: The maximum number of subqueries.
        """
        self._k = k
        
        tool_name = "examples_retriever"
        tool_description = (
            "Retrieve relevant examples to guide the model's response.\n"
            "This tool is useful for finding specific instances, snippets, or precedents to inform\n"
            "the final answer, ensuring accuracy and consistency."
        )

        super().__init__(
            collection_instance= examples_collection,
            tool_name= tool_name,
            tool_description= tool_description,
            max_subqueries= max_subqueries
        )


    def run(self, queries: List[str]) -> List[str]:
        """
        Implements the retrieval logic for this tool.

        Args:
            queries: A list of search queries.

        Returns:
            A list of strings with the retrieved results.
        """
        search_results = self._collection.search(
            queries= queries,
            search_type= 'similarity_score_threshold',
            merge_results= True,
            k= self._k,
        )

        return search_results if search_results else [__NO_RELEVANT_RESULTS_MSG]



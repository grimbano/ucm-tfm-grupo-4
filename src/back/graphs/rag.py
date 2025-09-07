
import os
from abc import ABC, abstractmethod
from typing import Any, Optional, Tuple, Type, Union
from langgraph.typing import ContextT, InputT, NodeInputT, OutputT, StateT
from langchain.tools import BaseTool
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph, START, END

from .aux_graphs import ChunkProcessingGraph
from .base import BaseGraph
from .edges import SendToParallelGradingEdge
from .nodes import (
    BaseGenerateSubQueriesNode,
    BaseNode,
    BaseRetrieveToolNode,
    GenerateBusinessLogicSubQueriesNode,
    GenerateMdlSubQueriesNode,
    RetrieveBusinessLogicQueriesNode,
    RetrieveMdlQueriesNode,
    SummarizeBusinessLogicNode,
    SummarizeMdlNode,
)
from .states import (
    BusinessLogicOutputState,
    BusinessLogicState,
    MdlOutputState,
    MdlState,
)
from .tools import (
    BusinessLogicRetrieverTool,
    MdlRetrieverTool,
)
from ..embeddings import GenAIExtendedEmbeddingFunction
from ..chroma_collections import (
    ContextEnricherChromaCollection,
    ExtendedChromaCollection,
    MdlHierarchicalChromaCollections,
)

__VALID_CHROMA_COLLECTIONS = (
    MdlHierarchicalChromaCollections,
    ExtendedChromaCollection
)

embedding_function = GenAIExtendedEmbeddingFunction('gemini-embedding-001')


class BaseRetrievalGraph(BaseGraph, ABC):
    """
    An abstract base class for building and compiling LangGraph workflows for
    retrieval-augmented generation (RAG) tasks.
    """

    _SPLIT_QUERY_STATE = 'create_subqueries'
    _RETRIEVER_TOOL_STATE = 'retrieve_chunks'
    _SUMMARIZE_STATE = 'create_summary'

    @property
    @abstractmethod
    def _grade_retrieval_state_name(self) -> str:
        """Returns the name for the chunk processing node."""
        pass
    
    @property
    @abstractmethod
    def _get_default_state_schema(self) -> Type[StateT]:
        """Returns the default state schema for the graph."""
        pass

    @property
    @abstractmethod
    def _get_default_output_schema(self) -> Type[OutputT]:
        """Returns the default output schema for the graph."""
        pass

    @abstractmethod
    def _get_default_chroma_collection(self) -> ExtendedChromaCollection:
        """Returns the default Chroma collection instance."""
        pass
    
    @abstractmethod
    def _get_default_retriever_tool(self) -> BaseTool:
        """Returns the default retriever tool instance."""
        pass

    @abstractmethod
    def _get_default_generate_sub_queries_node(self) -> NodeInputT:
        """Returns the default sub-queries generation node instance."""
        pass

    @abstractmethod
    def _get_default_retrieve_queries_node(self) -> NodeInputT:
        """Returns the default queries retrieval node instance."""
        pass

    @abstractmethod
    def _get_default_create_summary_node(self) -> NodeInputT:
        """Returns the default summary creation node instance."""
        pass

    def __init__(
        self,
        collection_names: Union[str, Tuple[str, str]],
        chroma_collection: Optional[Union[MdlHierarchicalChromaCollections, ExtendedChromaCollection]] = None,
        retriever_tool: Optional[BaseTool] = None,
        generate_sub_queries_node: Optional[NodeInputT] = None,
        retrieve_queries_node: Optional[NodeInputT] = None,
        process_chunks_node: Optional[ChunkProcessingGraph] = None,
        create_summary_node: Optional[NodeInputT] = None,
        parallel_chunk_processing_edge: Optional[SendToParallelGradingEdge] = None,
        state_schema: Optional[Type[StateT]] = None,
        context_schema: Optional[Type[ContextT]] = None,
        input_schema: Optional[Type[InputT]] = None,
        output_schema: Optional[Type[OutputT]] = None,
    ):
        """Initializes the RetrievalGraph with its core components and schemas.

        This constructor sets up the foundational elements for a retrieval-augmented
        generation (RAG) graph, including vector stores, retrieval tools, and
        various nodes for processing and summarizing information. By accepting
        optional components, it allows for flexible and custom graph configurations.

        Args:
            collection_names: The name or names of the Chroma collections to be used
                for retrieval. This can be a single string for a simple collection or
                a tuple of strings for a hierarchical one (e.g., tables and columns).
            chroma_collection: An optional, pre-initialized Chroma collection instance.
                If not provided, a default one will be created based on `collection_names`.
            retriever_tool: An optional, pre-initialized LangChain tool for document
                retrieval. If not provided, a default retriever tool will be created.
            generate_sub_queries_node: An optional graph node responsible for generating
                multiple sub-queries from the initial user query. Defaults to a standard
                sub-query generation node if not specified.
            retrieve_queries_node: An optional graph node that executes the generated
                sub-queries against the vector store to retrieve relevant documents.
            process_chunks_node: An optional sub-graph (or graph node) that handles the
                parallel processing of retrieved document chunks, such as grading their
                relevance or filtering them.
            create_summary_node: An optional graph node that summarizes the final,
                relevant documents into a coherent response.
            parallel_chunk_processing_edge: An optional edge that directs the flow from
                the retrieval node to the parallel chunk processing node.
            state_schema: The Pydantic class defining the graph's state schema.
                Defaults to a standard state schema if not provided.
            context_schema: The Pydantic class defining the context schema, used for
                managing context information within the graph.
            input_schema: The Pydantic class defining the input data structure for the
                graph.
            output_schema: The Pydantic class defining the final output structure of
                the graph.
        """
        super().__init__(
            state_schema= state_schema or self._get_default_state_schema,
            context_schema= context_schema,
            input_schema= input_schema or self._get_default_state_schema,
            output_schema= output_schema or self._get_default_output_schema,
        )

        self._collection_names = collection_names
        self._chroma_collection = chroma_collection or self._get_default_chroma_collection()
        self._retriever_tool = retriever_tool or self._get_default_retriever_tool()
        
        self._generate_sub_queries_node = generate_sub_queries_node or self._get_default_generate_sub_queries_node()
        self._retrieve_queries_node = retrieve_queries_node or self._get_default_retrieve_queries_node()
        self._process_chunks_node = process_chunks_node or ChunkProcessingGraph()
        self._create_summary_node = create_summary_node or self._get_default_create_summary_node()
        
        self._parallel_chunk_processing_edge = (
            parallel_chunk_processing_edge
            or SendToParallelGradingEdge(
                state_class= self.state_schema,
                target_node_name= self._grade_retrieval_state_name
            )
        )


    @property
    def chroma_collection(self) -> Type[ExtendedChromaCollection]:
        """Getter for the Chroma collection."""
        return self._chroma_collection

    @chroma_collection.setter
    def chroma_collection(self, value: ExtendedChromaCollection):
        """Setter with validation for the Chroma collection."""
        if not isinstance(value, __VALID_CHROMA_COLLECTIONS):
            raise TypeError("'chroma_collection' must be an instance of a class derived of ExtendedChromaCollection.")
        self._chroma_collection = value


    @property
    def collection_names(self) -> Union[str, Tuple[str]]:
        """Getter for the collection names."""
        return self._collection_names

    @collection_names.setter
    def collection_names(self, value: Union[str, Tuple[str]]):
        """Setter with validation for the chroma collection."""
        if not isinstance(value, (str, tuple)):
            raise TypeError("'collection_names' must be a string or a tuple of strings.")
        self._collection_names = value


    @property
    def retriever_tool(self) -> BaseTool:
        """Getter for the retriever tool."""
        return self._retriever_tool

    @retriever_tool.setter
    def retriever_tool(self, value: BaseTool):
        """Setter with validation for the retriever tool."""
        if not isinstance(value, BaseTool):
            raise TypeError("'retriever_tool' must be an instance of BaseTool.")
        self._retriever_tool = value


    @property
    def generate_sub_queries_node(self) -> BaseGenerateSubQueriesNode:
        """Getter for the generate sub-queries node."""
        return self._generate_sub_queries_node

    @generate_sub_queries_node.setter
    def generate_sub_queries_node(self, value: BaseGenerateSubQueriesNode):
        """Setter with validation for the generate sub-queries node."""
        if not isinstance(value, BaseGenerateSubQueriesNode):
            raise TypeError("'generate_sub_queries_node' must be a BaseGenerateSubQueriesNode instance.")
        self._generate_sub_queries_node = value


    @property
    def retrieve_queries_node(self) -> BaseRetrieveToolNode:
        """Getter for the retrieve queries node."""
        return self._retrieve_queries_node

    @retrieve_queries_node.setter
    def retrieve_queries_node(self, value: BaseRetrieveToolNode):
        """Setter with validation for the retrieve queries node."""
        if not isinstance(value, BaseRetrieveToolNode):
            raise TypeError("'retrieve_queries_node' must be a BaseRetrieveToolNode instance.")
        self._retrieve_queries_node = value


    @property
    def process_chunks_node(self) -> ChunkProcessingGraph:
        """Getter for the chunk processing graph node."""
        return self._process_chunks_node

    @process_chunks_node.setter
    def process_chunks_node(self, value: ChunkProcessingGraph):
        """Setter with validation for the chunk processing graph node."""
        if not isinstance(value, ChunkProcessingGraph):
            raise TypeError("'process_chunks_node' must be a ChunkProcessingGraph instance.")
        self._process_chunks_node = value


    @property
    def create_summary_node(self) -> BaseNode:
        """Getter for the create summary node."""
        return self._create_summary_node

    @create_summary_node.setter
    def create_summary_node(self, value: BaseNode):
        """Setter with validation for the create summary node."""
        if not isinstance(value, BaseNode):
            raise TypeError("'create_summary_node' must be a BaseNode instance.")
        self._create_summary_node = value


    @property
    def parallel_chunk_processing_edge(self) -> SendToParallelGradingEdge:
        """Getter for the parallel chunk processing edge."""
        return self._parallel_chunk_processing_edge

    @parallel_chunk_processing_edge.setter
    def parallel_chunk_processing_edge(self, value: SendToParallelGradingEdge):
        """Setter with validation for the parallel chunk processing edge."""
        if not isinstance(value, SendToParallelGradingEdge):
            raise TypeError("'parallel_chunk_processing_edge' must be a SendToParallelGradingEdge instance.")
        self._parallel_chunk_processing_edge = value


    def get_compiled_graph(self) -> CompiledStateGraph[Optional[Any]]:
        """
        Builds and compiles the LangGraph workflow.
        """
        print(f"--- BUILDING {self.__class__.__name__.upper()} GRAPH 🏗️ ---")

        workflow = StateGraph(
            state_schema= self.state_schema,
            context_schema= self.context_schema,
            input_schema= self.input_schema,
            output_schema= self.output_schema,
        )

        workflow.add_node(
            self._SPLIT_QUERY_STATE,
            self._generate_sub_queries_node.get_node_function()
        )
        workflow.add_node(
            self._RETRIEVER_TOOL_STATE,
            self._retrieve_queries_node.get_node_function()
        )
        workflow.add_node(
            self._grade_retrieval_state_name,
            self._process_chunks_node.get_compiled_graph()
        )
        workflow.add_node(
            self._SUMMARIZE_STATE,
            self._create_summary_node.get_node_function()
        )

        workflow.add_edge(START, self._SPLIT_QUERY_STATE)
        workflow.add_edge(self._SPLIT_QUERY_STATE, self._RETRIEVER_TOOL_STATE)
        workflow.add_conditional_edges(
            self._RETRIEVER_TOOL_STATE,
            self._parallel_chunk_processing_edge.get_edge_function(),
            [self._grade_retrieval_state_name]
        )
        workflow.add_edge(self._grade_retrieval_state_name, self._SUMMARIZE_STATE)
        workflow.add_edge(self._SUMMARIZE_STATE, END)
        
        compiled_graph = workflow.compile()
        print(f"--- {self.__class__.__name__.upper()} COMPILED SUCCESSFULLY ✅ ---")

        return compiled_graph



class BusinessLogicRetrievalGraph(BaseRetrievalGraph):
    """
    A class to build and compile a LangGraph workflow for retrieving and summarizing
    business logic-related information.

    The graph's workflow includes:
    1. Generating sub-queries for effective retrieval.
    2. Retrieving relevant chunks of information.
    3. Processing these chunks in parallel for relevance and summary generation.
    4. Summarizing the validated chunks into a final, coherent response.
    """
    
    _grade_retrieval_state_name = 'process_business_logic_chunks'


    def __init__(
        self,
        collection_name: str = 'business_logic',
        **kwargs
    ):
        """Initializes the BusinessLogicRetrievalGraph.

        This constructor sets up a retrieval graph configured for business logic
        data. It inherits the core graph functionality from `BaseRetrievalGraph`
        and specializes it for a single Chroma collection.

        Args:
            collection_name: The name of the Chroma collection to be used for storing
                    and retrieving business logic documents. **Defaults to 'business_logic'.**
            **kwargs: Additional keyword arguments passed to the `BaseRetrievalGraph`
                    constructor, allowing for flexible configuration of components like
                    nodes, tools, and schemas.
        """
        super().__init__(collection_names=collection_name, **kwargs)


    @property
    def _get_default_state_schema(self) -> Type[BusinessLogicState]:
        return BusinessLogicState

    @property
    def _get_default_output_schema(self) -> Type[BusinessLogicOutputState]:
        return BusinessLogicOutputState


    def _get_default_chroma_collection(self) -> ContextEnricherChromaCollection:
        return ContextEnricherChromaCollection(
            collection_name= self.collection_names,
            embedding_function= embedding_function,
            host= os.getenv('CHROMA_SERVER_HOST'),
            port= os.getenv('CHROMA_LOCAL_PORT')
        )

    def _get_default_retriever_tool(self) -> BaseTool:
        return BusinessLogicRetrieverTool(self.chroma_collection).tool_instance

    def _get_default_generate_sub_queries_node(self) -> GenerateBusinessLogicSubQueriesNode:
        return GenerateBusinessLogicSubQueriesNode(self.state_schema)

    def _get_default_retrieve_queries_node(self) -> RetrieveBusinessLogicQueriesNode:
        return RetrieveBusinessLogicQueriesNode(self.retriever_tool, self.state_schema)

    def _get_default_create_summary_node(self) -> SummarizeBusinessLogicNode:
        return SummarizeBusinessLogicNode(state_class=self.state_schema)



class MdlRetrievalGraph(BaseRetrievalGraph):
    """
    A class to build and compile a LangGraph workflow for retrieving and summarizing
    MDL Data Schema information.

    The graph's workflow includes:
    1. Generating sub-queries for effective retrieval.
    2. Retrieving relevant chunks of information.
    3. Processing these chunks in parallel for relevance and summary generation.
    4. Summarizing the validated chunks into a final, coherent response.
    """

    _grade_retrieval_state_name = 'process_data_schema_chunks'


    def __init__(
        self,
        collection_names: Tuple[str, str] = ('mdl_tables_summary', 'mdl_columns'),
        **kwargs
    ):
        """Initializes the MdlRetrievalGraph for hierarchical data.

        This constructor sets up a retrieval graph specifically for hierarchical
        data, such as database tables and their associated columns. It leverages
        the `BaseRetrievalGraph` for core functionality while providing specialized
        configuration for two interconnected Chroma collections.

        Args:
            collection_names: A tuple containing the names of the parent and child
                    Chroma collections. The first name is for the parent collection (e.g.,
                    table summaries), and the second is for the child collection (e.g.,
                    column details). **Defaults to ('mdl_tables_summary', 'mdl_columns').**
            **kwargs: Additional keyword arguments passed to the `BaseRetrievalGraph`
                    constructor, allowing for flexible configuration of components like
                    nodes, tools, and schemas.
        """
        super().__init__(collection_names=collection_names, **kwargs)


    @property
    def _get_default_state_schema(self) -> Type[MdlState]:
        return MdlState

    @property
    def _get_default_output_schema(self) -> Type[MdlOutputState]:
        return MdlOutputState


    def _get_default_chroma_collection(self) -> MdlHierarchicalChromaCollections:
        return MdlHierarchicalChromaCollections(
            collection_names= ('mdl_tables_summary', 'mdl_columns'),
            embedding_function= embedding_function,
            host= os.getenv('CHROMA_SERVER_HOST'),
            port= os.getenv('CHROMA_LOCAL_PORT')
        )

    def _get_default_retriever_tool(self) -> BaseTool:
        return MdlRetrieverTool(self.chroma_collection).tool_instance

    def _get_default_generate_sub_queries_node(self) -> GenerateMdlSubQueriesNode:
        return GenerateMdlSubQueriesNode(self.state_schema)

    def _get_default_retrieve_queries_node(self) -> RetrieveMdlQueriesNode:
        return RetrieveMdlQueriesNode(self.retriever_tool, self.state_schema)

    def _get_default_create_summary_node(self) -> SummarizeMdlNode:
        return SummarizeMdlNode(state_class=self.state_schema)
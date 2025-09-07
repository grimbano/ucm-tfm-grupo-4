
from typing import Any, Optional, Type
from langgraph.typing import ContextT, InputT, OutputT, StateT
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph, START, END

from .base import BaseGraph
from .edges import BaseEdge, RouteContextRelevanceEdge
from .nodes import (
    BaseNode,
    DefineUserQueryLanguageNode,
    GenerateGlobalContextNode,
    GenerateNoContextResponseNode,
    GradeContextSummariesNode
)
from .rag import (
    BaseRetrievalGraph,
    BusinessLogicRetrievalGraph,
    MdlRetrievalGraph
)
from .states import (
    ContextGeneratorOutputState,
    ContextGeneratorState
)


class ContextGeneratorGraph(BaseGraph):
    """
    A class to build and compile a LangGraph workflow for generating context
    from multiple retrieval-augmented generation (RAG) sources.

    The graph's workflow includes:
    1. Detecting the user query's language.
    2. Retrieving and summarizing business logic and data schema information
        in parallel.
    3. Grading the generated summaries for relevance and hallucinations.
    4. If relevant, generating a final, consolidated global context.
    5. If not relevant, generating a "no relevance" response.
    """

    _DETECT_LANGUAGE_STATE = 'detect_user_query_language'
    _BUSINESS_LOGIC_STATE = 'get_business_logic_summary'
    _DATA_SCHEMA_STATE = 'get_data_schema_summary'
    _GRADE_SUMMARIES_STATE = 'grade_context_summaries'
    _GENERATE_GLOBAL_CONTEXT_STATE = 'generate_global_context'
    _NO_RELEVANCE_RESPONSE_STATE = 'generate_no_relevance_response'


    def __init__(
        self,
        detect_language_node: Optional[BaseNode] = None,
        business_logic_node: Optional[BaseRetrievalGraph] = None,
        data_schema_node: Optional[BaseRetrievalGraph] = None,
        grade_summaries_node: Optional[BaseNode] = None,
        global_context_node: Optional[BaseNode] = None,
        no_relevance_node: Optional[BaseNode] = None,
        check_relevance_edge: Optional[BaseEdge] = None,
        state_schema: Optional[Type[StateT]] = None,
        context_schema: Optional[Type[ContextT]] = None,
        input_schema: Optional[Type[InputT]] = None,
        output_schema: Optional[Type[OutputT]] = None,
    ):
        """Initializes the ContextGeneratorGraph with its core components.

        This constructor sets up the graph's nodes and edges, using default
        implementations if none are provided.

        Args:
            detect_language_node: An optional node to detect the language of the query.
            business_logic_node: An optional pre-initialized graph for business logic retrieval.
            data_schema_node: An optional pre-initialized graph for data schema retrieval.
            grade_summaries_node: An optional node to grade the relevance of retrieved summaries.
            global_context_node: An optional node to generate the final consolidated context.
            no_relevance_node: An optional node to handle cases with no relevant retrieved context.
            check_relevance_edge: An optional conditional edge to route the workflow
                based on the summaries' relevance.
            state_schema: The schema for the graph's state.
            context_schema: Optional schema for contextual information.
            input_schema: Optional schema for the graph's input.
            output_schema: Optional schema for the graph's output.
        """
        super().__init__(
            state_schema= state_schema or ContextGeneratorState,
            context_schema= context_schema,
            input_schema= input_schema or ContextGeneratorState,
            output_schema= output_schema or ContextGeneratorOutputState,
        )

        self._detect_language_node = (
            detect_language_node
            or DefineUserQueryLanguageNode(self.state_schema)
        )

        self._business_logic_node = (
            business_logic_node
            or BusinessLogicRetrievalGraph()
        )

        self._data_schema_node = (
            data_schema_node
            or MdlRetrievalGraph()
        )

        self._grade_summaries_node = (
            grade_summaries_node
            or GradeContextSummariesNode(self.state_schema)
        )

        self._global_context_node = (
            global_context_node
            or GenerateGlobalContextNode(self.state_schema)
        )

        self._no_relevance_node = (
            no_relevance_node
            or GenerateNoContextResponseNode(self.state_schema)
        )

        self._check_relevance_edge = (
            check_relevance_edge
            or RouteContextRelevanceEdge(
                relevance_state_variable= GradeContextSummariesNode._output_property,
                is_relevant_next_step= self._GENERATE_GLOBAL_CONTEXT_STATE,
                no_relevance_next_step= self._NO_RELEVANCE_RESPONSE_STATE
            )
        )


    @property
    def detect_language_node(self) -> BaseNode:
        """Getter for the detect_language_node."""
        return self._detect_language_node

    @detect_language_node.setter
    def detect_language_node(self, value: BaseNode):
        """Setter with validation for the detect_language_node."""
        if not isinstance(value, BaseNode):
            raise TypeError("'detect_language_node' must be a BaseNode instance.")
        self._detect_language_node = value


    @property
    def business_logic_node(self) -> BaseRetrievalGraph:
        """Getter for the business_logic_node."""
        return self._business_logic_node

    @business_logic_node.setter
    def business_logic_node(self, value: BaseRetrievalGraph):
        """Setter with validation for the business_logic_node."""
        if not isinstance(value, BaseRetrievalGraph):
            raise TypeError("'business_logic_node' must be a BaseRetrievalGraph instance.")
        self._business_logic_node = value


    @property
    def data_schema_node(self) -> BaseRetrievalGraph:
        """Getter for the data_schema_node."""
        return self._data_schema_node

    @data_schema_node.setter
    def data_schema_node(self, value: BaseRetrievalGraph):
        """Setter with validation for the data_schema_node."""
        if not isinstance(value, BaseRetrievalGraph):
            raise TypeError("'data_schema_node' must be a BaseRetrievalGraph instance.")
        self._data_schema_node = value


    @property
    def grade_summaries_node(self) -> BaseNode:
        """Getter for the grade_summaries_node."""
        return self._grade_summaries_node

    @grade_summaries_node.setter
    def grade_summaries_node(self, value: BaseNode):
        """Setter with validation for the grade_summaries_node."""
        if not isinstance(value, BaseNode):
            raise TypeError("'grade_summaries_node' must be a BaseNode instance.")
        self._grade_summaries_node = value


    @property
    def global_context_node(self) -> BaseNode:
        """Getter for the global_context_node."""
        return self._global_context_node

    @global_context_node.setter
    def global_context_node(self, value: BaseNode):
        """Setter with validation for the global_context_node."""
        if not isinstance(value, BaseNode):
            raise TypeError("'global_context_node' must be a BaseNode instance.")
        self._global_context_node = value


    @property
    def no_relevance_node(self) -> BaseNode:
        """Getter for the no_relevance_node."""
        return self._no_relevance_node

    @no_relevance_node.setter
    def no_relevance_node(self, value: BaseNode):
        """Setter with validation for the no_relevance_node."""
        if not isinstance(value, BaseNode):
            raise TypeError("'no_relevance_node' must be a BaseNode instance.")
        self._no_relevance_node = value


    @property
    def check_relevance_edge(self) -> RouteContextRelevanceEdge:
        """Getter for the check_relevance_edge."""
        return self._check_relevance_edge

    @check_relevance_edge.setter
    def check_relevance_edge(self, value: RouteContextRelevanceEdge):
        """Setter with validation for the check_relevance_edge."""
        if not isinstance(value, RouteContextRelevanceEdge):
            raise TypeError("'check_relevance_edge' must be a RouteContextRelevanceEdge instance.")
        self._check_relevance_edge = value


    def get_compiled_graph(self) -> CompiledStateGraph[Optional[Any]]:
        """
        Builds and compiles the LangGraph workflow for context generation.

        Returns:
            The compiled LangGraph graph ready for execution.
        """
        print(f"--- BUILDING CONTEXT GENERATOR GRAPH 🏗️ ---")

        workflow = StateGraph(
            state_schema= self.state_schema,
            context_schema= self.context_schema,
            input_schema= self.input_schema,
            output_schema= self.output_schema,
        )


        workflow.add_node(
            self._DETECT_LANGUAGE_STATE,
            self.detect_language_node.get_node_function()
        )

        if self.business_logic_node and self.data_schema_node:
            workflow.add_node(
                self._BUSINESS_LOGIC_STATE,
                self.business_logic_node.get_compiled_graph()
            )
            workflow.add_node(
                self._DATA_SCHEMA_STATE,
                self.data_schema_node.get_compiled_graph()
            )
        else:
            raise ValueError("Both business logic and data schema graphs must be provided.")
        
        workflow.add_node(
            self._GRADE_SUMMARIES_STATE,
            self.grade_summaries_node.get_node_function()
        )
        workflow.add_node(
            self._GENERATE_GLOBAL_CONTEXT_STATE,
            self.global_context_node.get_node_function()
        )
        workflow.add_node(
            self._NO_RELEVANCE_RESPONSE_STATE,
            self.no_relevance_node.get_node_function()
        )


        workflow.add_edge(START, self._DETECT_LANGUAGE_STATE)
        workflow.add_edge(self._DETECT_LANGUAGE_STATE, self._BUSINESS_LOGIC_STATE)
        workflow.add_edge(self._DETECT_LANGUAGE_STATE, self._DATA_SCHEMA_STATE)
        workflow.add_edge(self._BUSINESS_LOGIC_STATE, self._GRADE_SUMMARIES_STATE)
        workflow.add_edge(self._DATA_SCHEMA_STATE, self._GRADE_SUMMARIES_STATE)
        workflow.add_conditional_edges(
            source= self._GRADE_SUMMARIES_STATE,
            path= self.check_relevance_edge.get_edge_function(),
            path_map= {
                self.check_relevance_edge.is_relevant_next_step: self._GENERATE_GLOBAL_CONTEXT_STATE,
                self.check_relevance_edge.no_relevance_next_step: self._NO_RELEVANCE_RESPONSE_STATE
            }
        )
        workflow.add_edge(self._GENERATE_GLOBAL_CONTEXT_STATE, END)
        workflow.add_edge(self._NO_RELEVANCE_RESPONSE_STATE, END)


        compiled_graph = workflow.compile()
        print(f"--- CONTEXT GENERATOR COMPILED SUCCESSFULLY ✅ ---")

        return compiled_graph

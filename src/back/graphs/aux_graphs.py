
from typing import Any, Optional, Type
from langgraph.typing import ContextT, InputT, NodeInputT, OutputT, StateT
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph, START, END

from .base import BaseGraph
from .states import (
    ChunkProcessingOutputState,
    ChunkProcessingState
)
from .nodes import (
    SetRetrievalGradeOutputKoNode,
    SummarizeChunkNode,
)
from .edges import (
    BaseEdge,
    GradeChunkSummaryGenerationEdge,
    GradeRetrievedChunkEdge
)

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ChunkProcessingGraph(BaseGraph):
    """
    A class to build and compile a LangGraph workflow for processing a single
    chunk of retrieved context.

    The graph's workflow is as follows:
    1. A single chunk of data is processed.
    2. An agent grades the chunk for relevance to the user's query.
    3. If relevant, the chunk is summarized.
    4. The summary is then graded to check for hallucinations and to ensure
        it addresses the user's query.
    5. The process can loop to generate a better summary if needed.
    """

    _SUMMARIZE_CHUNK_STATE = 'summarize_chunk'
    _KO_STATE = 'set_output_ko'

    def __init__(
        self,
        summarize_chunk_node: Optional[NodeInputT] = None,
        set_output_ko_node: Optional[NodeInputT] = None,
        grade_chunk_relevance_edge: Optional[BaseEdge] = None,
        grade_chunk_summary_edge: Optional[BaseEdge] = None,
        state_schema: Optional[Type[StateT]] = None,
        context_schema: Optional[Type[ContextT]] = None,
        input_schema: Optional[Type[InputT]] = None,
        output_schema: Optional[Type[OutputT]] = None,
    ):
        """
        Initializes the ChunkProcessingGraph with its core components and schemas.

        Args:
            summarize_chunk_node: The node responsible for summarizing a chunk.
            set_output_ko_node: A fallback node to handle non-relevant content.
            grade_chunk_relevance_edge: The conditional edge to grade chunk relevance.
            grade_chunk_summary_edge: The conditional edge to grade the generated summary.
            state_schema: The schema representing the graph's state.
            context_schema: Optional schema for contextual information.
            input_schema: Optional schema for the graph's input.
            output_schema: Optional schema for the graph's output.
        """
        super().__init__(
            state_schema= state_schema or ChunkProcessingState,
            context_schema= context_schema,
            input_schema= input_schema or ChunkProcessingState,
            output_schema= output_schema or ChunkProcessingOutputState,
        )

        self._summarize_chunk_node = (
            summarize_chunk_node 
            or SummarizeChunkNode(state_class= self.state_schema)
        )
        self._set_output_ko_node = (
            set_output_ko_node
            or SetRetrievalGradeOutputKoNode()
        )
        self._grade_chunk_relevance_edge = (
            grade_chunk_relevance_edge or
            GradeRetrievedChunkEdge(
                state_class= self.state_schema,
                is_relevant_next_step= self._SUMMARIZE_CHUNK_STATE,
                no_relevance_next_step= self._KO_STATE
            )
        )
        self._grade_chunk_summary_edge = (
            grade_chunk_summary_edge
            or GradeChunkSummaryGenerationEdge(
                state_class= self.state_schema,
                retry_next_step= self._SUMMARIZE_CHUNK_STATE,
                abort_next_step= self._KO_STATE
            )
        )


    @property
    def summarize_chunk_node(self) -> NodeInputT:
        """Getter for the summarize_chunk_node."""
        return self._summarize_chunk_node

    @summarize_chunk_node.setter
    def summarize_chunk_node(self, value: NodeInputT):
        """Setter with validation for the summarize_chunk_node."""
        if not isinstance(value, NodeInputT):
            raise TypeError("'summarize_chunk_node' must be an instance of NodeInputT.")
        self._summarize_chunk_node = value


    @property
    def set_output_ko_node(self) -> NodeInputT:
        """Getter for the set_output_ko_node."""
        return self._set_output_ko_node

    @set_output_ko_node.setter
    def set_output_ko_node(self, value: NodeInputT):
        """Setter with validation for the set_output_ko_node."""
        if not isinstance(value, NodeInputT):
            raise TypeError("'set_output_ko_node' must be an instance of NodeInputT.")
        self._set_output_ko_node = value


    @property
    def grade_chunk_relevance_edge(self) -> BaseEdge:
        """Getter for the grade_chunk_relevance_edge."""
        return self._grade_chunk_relevance_edge

    @grade_chunk_relevance_edge.setter
    def grade_chunk_relevance_edge(self, value: BaseEdge):
        """Setter with validation for the grade_chunk_relevance_edge."""
        if not isinstance(value, BaseEdge):
            raise TypeError("'grade_chunk_relevance_edge' must be an instance of BaseEdge.")
        self._grade_chunk_relevance_edge = value


    @property
    def grade_chunk_summary_edge(self) -> BaseEdge:
        """Getter for the grade_chunk_summary_edge."""
        return self._grade_chunk_summary_edge

    @grade_chunk_summary_edge.setter
    def grade_chunk_summary_edge(self, value: BaseEdge):
        """Setter with validation for the grade_chunk_summary_edge."""
        if not isinstance(value, BaseEdge):
            raise TypeError("'grade_chunk_summary_edge' must be an instance of BaseEdge.")
        self._grade_chunk_summary_edge = value


    def get_compiled_graph(self) -> CompiledStateGraph[Optional[Any]]:   
        """
        Builds and compiles the LangGraph graph.

        This method defines the graph's structure by adding nodes and connecting
        them with edges, including conditional routing and parallel processing.

        Returns:
            The compiled LangGraph graph ready for execution.
        """
        logging.info("--- BUILDING CHUNK PROCESSING GRAPH 🏗️ ---")

        workflow = StateGraph(
            state_schema= self.state_schema,
            context_schema= self.context_schema,
            input_schema= self.input_schema,
            output_schema= self.output_schema,
        )

        workflow.add_node(
            self._SUMMARIZE_CHUNK_STATE,
            self.summarize_chunk_node.get_node_function()
        )
        workflow.add_node(
            self._KO_STATE,
            self.set_output_ko_node.get_node_function()
        )

        workflow.add_conditional_edges(
            source= START,
            path= self.grade_chunk_relevance_edge.get_edge_function(),
            path_map= {
                self.grade_chunk_relevance_edge.is_relevant_next_step: self._SUMMARIZE_CHUNK_STATE,
                self.grade_chunk_relevance_edge.no_relevance_next_step: self._KO_STATE
            }
        )
        workflow.add_conditional_edges(
            source= self._SUMMARIZE_CHUNK_STATE,
            path= self.grade_chunk_summary_edge.get_edge_function(),
            path_map= {
                self.grade_chunk_summary_edge.retry_next_step: self._SUMMARIZE_CHUNK_STATE,
                self.grade_chunk_summary_edge.abort_next_step: self._KO_STATE,
                '__end__': END
            }
        )
        workflow.add_edge(self._KO_STATE, END)


        compiled_graph = workflow.compile()
        logging.info("--- CHUNK PROCESSING GRAPH COMPILED SUCCESSFULLY ⚙️✅ ---")

        return compiled_graph


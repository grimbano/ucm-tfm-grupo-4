
from typing import Any, Optional
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph, START, END

from .nodes import (
    DefineUserQueryLanguageNode,
    GradeBusinessRelevanceNode,
    GenerateFinalOutputNode,
)
from .edges import RouteBooleanStateVariableEdge
from .states import MainGraphState, MainGraphOutputState
from .conclusions_generator import get_conclusions_generator_graph
from .context_generator import ContextGeneratorGraph
from .query_generator import get_query_generator_graph
from .query_validator import get_query_validator_graph


def get_main_graph() -> CompiledStateGraph[Optional[Any]]:

    workflow = StateGraph(
        state_schema= MainGraphState,
        input_schema= MainGraphState,
        output_schema= MainGraphOutputState
    )

    workflow.add_node(
        'detect_user_query_language',
        DefineUserQueryLanguageNode(MainGraphState).get_node_function()
    )
    workflow.add_node(
        'grade_question_relevance',
        GradeBusinessRelevanceNode(MainGraphState).get_node_function()
    )
    workflow.add_node(
        'context_generator',
        ContextGeneratorGraph().get_compiled_graph()
    )
    workflow.add_node(
        'query_generator',
        get_query_generator_graph()
    )
    workflow.add_node(
        'query_validator',
        get_query_validator_graph()
    )
    workflow.add_node(
        'conclusions_generator',
        get_conclusions_generator_graph()
    )
    workflow.add_node(
        'structure_final_output',
        GenerateFinalOutputNode(MainGraphState).get_node_function()
    )

    workflow.add_edge(START, 'detect_user_query_language')
    workflow.add_edge('detect_user_query_language', 'grade_question_relevance')
    workflow.add_conditional_edges(
        'grade_question_relevance',
        RouteBooleanStateVariableEdge(
            'relevant_question',
            'continue',
            'exit'
        ).get_edge_function(),
        {
            'continue': 'context_generator',
            'exit': 'structure_final_output'
        }
    )
    workflow.add_conditional_edges(
        'context_generator',
        RouteBooleanStateVariableEdge(
            'relevant_context',
            'continue',
            'exit'
        ).get_edge_function(),
        {
            'continue': 'query_generator',
            'exit': 'structure_final_output'
        }
    )
    workflow.add_conditional_edges(
        'query_generator',
        RouteBooleanStateVariableEdge(
            'valid_query_generated',
            'continue',
            'exit'
        ).get_edge_function(),
        {
            'continue': 'query_validator',
            'exit': 'structure_final_output'
        }
    )
    workflow.add_conditional_edges(
        'query_validator',
        RouteBooleanStateVariableEdge(
            'valid_query_execution',
            'continue',
            'exit'
        ).get_edge_function(),
        {
            'continue': 'conclusions_generator',
            'exit': 'structure_final_output'
        }
    )
    workflow.add_edge('conclusions_generator', 'structure_final_output')
    workflow.add_edge('structure_final_output', END)

    compiled_graph = workflow.compile()
    print(f"--- MAIN GRAPH COMPILED SUCCESSFULLY ✅ ---")

    return compiled_graph
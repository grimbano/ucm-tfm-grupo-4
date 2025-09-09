
from typing import Any, Optional
from langgraph.graph import StateGraph
from langgraph.graph.state import CompiledStateGraph, START, END

from .nodes import DefineUserQueryLanguageNode
from .edges import RouteBooleanStateVariableEdge
from .states import MainGraphState
from .context_generator import ContextGeneratorGraph
from .query_generator import get_query_generator_graph


def get_main_graph() -> CompiledStateGraph[Optional[Any]]:

    workflow = StateGraph(
        state_schema= MainGraphState,
        input_schema= MainGraphState,
        # output_schema= QueryGeneratorOutputState
    )

    workflow.add_node(
        'detect_user_query_language',
        DefineUserQueryLanguageNode(MainGraphState).get_node_function()
    )
    workflow.add_node(
        'context_generator',
        ContextGeneratorGraph().get_compiled_graph()
    )
    workflow.add_node(
        'query_generator',
        get_query_generator_graph()
    )

    workflow.add_edge(START, 'detect_user_query_language')
    workflow.add_edge('detect_user_query_language', 'context_generator')
    workflow.add_conditional_edges(
        "context_generator",
        RouteBooleanStateVariableEdge(
            'relevant_context',
            'continue',
            'exit'
        ).get_edge_function(),
        {
            'continue': 'query_generator',
            'exit': END
        }
    )
    workflow.add_edge('query_generator', END)

    compiled_graph = workflow.compile()
    print(f"--- MAIN GRAPH COMPILED SUCCESSFULLY ✅ ---")

    return compiled_graph
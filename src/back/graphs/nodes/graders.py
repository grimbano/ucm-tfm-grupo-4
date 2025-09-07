
from typing import Any, Callable, Dict

from .base import BaseNode
from ..agents import GlobalRetrievalGrader



class GradeContextSummariesNode(BaseNode):
    """
    A node that grades the relevance of retrieved context summaries.

    This class specializes `BaseNode` to evaluate if the retrieved business logic and
    MDL context are relevant to the user's query and useful for further generation.
    """

    _agent_validation_Type = 'structured_output'
    _required_state_vars = [
        'user_query',
        'business_logic',
        'data_schema',
        'relevant_context'
    ]
    _output_property  = 'relevant_context'


    def get_default_agent(self) -> GlobalRetrievalGrader:
        """
        Provides a new default retrieval grader agent for this node.
        
        Returns:
            A new instance of RetrievalGrader.
        """
        return GlobalRetrievalGrader()


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.

        Returns:
            A function that takes the state dictionary and returns an updated state.
        """

        agent_runnable = self.agent.get_runnable()

        def grade_context_summaries(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Determines whether the generation is grounded in the document and informative for the question.

            Args:
                state: The current graph state.

            Returns:
                An updated state dictionary containing the consolidated context summary and the grading result.
            """
            print("--- GRADE CONTEXT SUMMARIES 🔍 ---")
            
            user_query = state['user_query']
            business_logic = state['business_logic']
            data_schema = state['data_schema']

            relevant_context = getattr(
                agent_runnable.invoke({
                    'user_query': user_query,
                    'business_logic': business_logic,
                    'data_schema': data_schema,
                }),
                self.output_property
            )

            return {
                'relevant_context': relevant_context,
            }

        return grade_context_summaries



from typing import Any, Callable, Dict

from .base import BaseNode
from ..agents import LanguageClassifier



class DefineUserQueryLanguageNode(BaseNode):
    """
    A node that defines the language of a user query.
    """

    _agent_validation_Type = 'structured_output'
    _required_state_vars = [
        'user_query', 'language',
        'context_generation_iterations'
    ]
    _output_property = 'language'


    def get_default_agent(self) -> LanguageClassifier:
        """
        Provides a new default language classifier agent for this node.
        
        Returns:
            A new instance of LanguageClassifier.
        """
        return LanguageClassifier()


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.

        Returns:
            A function that takes the state dictionary and returns an updated state.
        """
        
        agent_runnable = self.agent.get_runnable()

        def define_user_query_language(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Define the language of the user query.

            Args:
                state: The current graph state.

            Returns:
                An updated state dictionary containing the detected language and
                an incremented iteration count.
            """
            print("--- DEFINE USER QUERY LANGUAGE 🔣 ---")
            
            user_query = state['user_query']
            context_generation_iterations = state.get('context_generation_iterations', 0)
            
            language = getattr(
                agent_runnable.invoke({'user_query': user_query}),
                self.output_property
            )

            return {
                'language': language,
                'context_generation_iterations': context_generation_iterations + 1,
            }

        return define_user_query_language


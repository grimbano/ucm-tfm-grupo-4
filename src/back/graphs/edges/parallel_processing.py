
from typing import Any, Callable, Dict, List, Optional, Type
from langgraph.graph.state import Send

from .base import BaseEdge


class SendToParallelGradingEdge(BaseEdge):
    """
    A conditional edge node that generates a list of `Send` instructions 
    for parallel execution based on retrieval results.
    """

    _required_state_vars = [
        'user_query', 'language', 
        'entity', 'retrieval_results'
    ]

    def __init__(
        self,
        state_class: Type[Dict],
        target_node_name: str,
        required_state_vars: Optional[List[str]] = None,
    ):
        """
        Initializes the node with its dependencies.
        Args:
            state_class: The TypedDict class for state validation.
            target_node_name: The name of the node to send the state to.
            required_state_vars: An optional list of required state variables.
        """
        super().__init__(
            state_class= state_class,
            required_state_vars= required_state_vars
        )

        if not isinstance(target_node_name, str) or not target_node_name.strip():
            raise ValueError("'target_node_name' must be a non-empty string.")
        self._target_node_name = target_node_name


    @property
    def target_node_name(self) -> str:
        """Getter for the 'target_node_name' property."""
        return self._target_node_name

    @target_node_name.setter
    def target_node_name(self, value: str):
        """Setter for the 'target_node_name' property with validation."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError("'target_node_name' must be a non-empty string.")
        self._target_node_name = value


    def get_edge_function(self) -> Callable[[Dict[str, Any]], List[Send]]:
        """
        Returns the callable function for this conditional edge.
        """
        def send_to_parallel_grading(state: Dict[str, Any]) -> List[Send]:
            """
            Conditional edge to reach generation parallelization.

            Args:
                state: The current graph state
            """
            print("--- PARALLELIZE GENERATION 🔢 ---")

            user_query = state['user_query']
            language = state['language']
            entity = state['entity']
            retrieval_results = state['retrieval_results']

            return [
                Send(self.target_node_name, {
                    'user_query': user_query,
                    'language': language,
                    'chunk_txt': chunk_txt,
                    'entity': entity
                })
                for chunk_txt in retrieval_results
            ]
        
        return send_to_parallel_grading


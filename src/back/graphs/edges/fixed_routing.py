
from typing import Any, Callable, Dict, Union



class RouteBooleanStateVariableEdge:
    """
    A conditional edge node that routes the flow based on a boolean state variable.
    """
    def __init__(
        self,
        relevance_state_variable: str,
        is_relevant_next_step: Union[str, bool],
        no_relevance_next_step: Union[str, bool]
    ):
        """
        Initializes the node with its dependencies and configurable routing parameters.

        Args:
            relevance_state_variable: The key in the state dictionary to check.
            is_relevant_next_step: The node to call if the state variable is True.
            no_relevance_next_step: The node to call if the state variable is False.
        """
        if not isinstance(relevance_state_variable, str):
            raise TypeError("relevance_state_variable must be a string.")
        self._relevance_state_variable = relevance_state_variable

        if not isinstance(is_relevant_next_step, (str, bool)):
            raise TypeError("is_relevant_next_step must be a string or bool.")
        self._is_relevant_next_step = is_relevant_next_step

        if not isinstance(no_relevance_next_step, (str, bool)):
            raise TypeError("no_relevance_next_step must be a string or bool.")
        self._no_relevance_next_step = no_relevance_next_step


    @property
    def relevance_state_variable(self) -> str:
        """Getter for the relevance_state_variable property."""
        return self._relevance_state_variable

    @relevance_state_variable.setter
    def relevance_state_variable(self, value: str):
        """Setter for the relevance_state_variable property."""
        if not isinstance(value, str):
            raise TypeError("relevance_state_variable must be a string.")
        self._relevance_state_variable = value


    @property
    def is_relevant_next_step(self) -> Union[str, bool]:
        """Getter for the is_relevant_next_step property."""
        return self._is_relevant_next_step

    @is_relevant_next_step.setter
    def is_relevant_next_step(self, value: Union[str, bool]):
        """Setter for the is_relevant_next_step property."""
        if not isinstance(value, (str, bool)):
            raise TypeError("is_relevant_next_step must be a string or bool.")
        self._is_relevant_next_step = value


    @property
    def no_relevance_next_step(self) -> Union[str, bool]:
        """Getter for the no_relevance_next_step property."""
        return self._no_relevance_next_step

    @no_relevance_next_step.setter
    def no_relevance_next_step(self, value: Union[str, bool]):
        """Setter for the no_relevance_next_step property."""
        if not isinstance(value, (str, bool)):
            raise TypeError("no_relevance_next_step must be a string or bool.")
        self._no_relevance_next_step = value


    def get_edge_function(self) -> Callable[[Dict[str, Any]], str]:
        """
        Returns the callable function for this conditional edge.
        """
        def route_context_relevance(state: Dict[str, Any]) -> str:
            """
            Routes the flow based on a boolean state variable.
            """
            if not isinstance(state[self.relevance_state_variable], bool):
                TypeError(f"'{self.relevance_state_variable}' in state must be a bool.")

            return (
                self.is_relevant_next_step
                if state[self.relevance_state_variable] else
                self.no_relevance_next_step
            )

        return route_context_relevance


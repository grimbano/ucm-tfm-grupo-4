
from typing import Optional, Type
from langgraph.typing import ContextT, InputT, NodeInputT, OutputT, StateT


class BaseGraph:
    """
    A base class for building and managing a LangGraph graph.

    This class encapsulates the core components and schema definitions
    for a graph's state, input, and output.
    """

    def __init__(
        self,
        state_schema: Type[StateT],
        context_schema: Optional[Type[ContextT]] = None,
        input_schema: Optional[Type[InputT]] = None,
        output_schema: Optional[Type[OutputT]] = None,
    ):
        """
        Initializes the graph with its schemas.

        Args:
            state_schema: The schema representing the graph's state.
            context_schema: An optional schema for the graph's context.
            input_schema: An optional schema for the graph's input.
            output_schema: An optional schema for the graph's output.
        """

        self._state_schema = state_schema
        self._context_schema = context_schema
        self._input_schema = input_schema
        self._output_schema = output_schema

    @property
    def state_schema(self) -> Type[StateT]:
        """Getter for the state schema."""
        return self._state_schema

    @state_schema.setter
    def state_schema(self, value: Type[StateT]):
        """Setter with validation for the state schema."""
        if not isinstance(value, type):
            raise TypeError("state_schema must be a class (type).")
        self._state_schema = value


    @property
    def context_schema(self) -> Optional[Type[ContextT]]:
        """Getter for the context schema."""
        return self._context_schema

    @context_schema.setter
    def context_schema(self, value: Optional[Type[ContextT]]):
        """Setter with validation for the context schema."""
        if value is not None and not isinstance(value, type):
            raise TypeError("context_schema must be a class (type) or None.")
        self._context_schema = value


    @property
    def input_schema(self) -> Optional[Type[InputT]]:
        """Getter for the input schema."""
        return self._input_schema

    @input_schema.setter
    def input_schema(self, value: Optional[Type[InputT]]):
        """Setter with validation for the input schema."""
        if value is not None and not isinstance(value, type):
            raise TypeError("input_schema must be a class (type) or None.")
        self._input_schema = value


    @property
    def output_schema(self) -> Optional[Type[OutputT]]:
        """Getter for the output schema."""
        return self._output_schema

    @output_schema.setter
    def output_schema(self, value: Optional[Type[OutputT]]):
        """Setter with validation for the output schema."""
        if value is not None and not isinstance(value, type):
            raise TypeError("output_schema must be a class (type) or None.")
        self._output_schema = value


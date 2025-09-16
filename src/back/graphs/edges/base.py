
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Literal, Optional, Type

from ..agents import BaseAgent


class BaseEdge(ABC):
    """
    A unified base class for all conditional edges in a graph.
    
    This class provides common functionality for edges, including state validation
    and an abstract method for defining the routing logic.
    """
    
    _required_state_vars: Optional[List[str]] = None
    
    def __init__(
        self, 
        state_class: Type[Dict],
        required_state_vars: Optional[List[str]] = None
    ):
        """
        Initializes the base edge and validates the state class.
        
        Args:
            state_class: The TypedDict class representing the graph state.
            required_state_vars: An optional list of required state variables.
        """
        self._required_state_vars = required_state_vars or self._required_state_vars

        if self._required_state_vars is not None:
            if not isinstance(self._required_state_vars, list):
                raise TypeError("required_state_vars must be a list.")
            if not all(isinstance(item, str) for item in self._required_state_vars):
                raise TypeError("All items in required_state_vars must be strings.")
        
        if not self._required_state_vars:
            raise TypeError("A list of required state variables must be provided.")

        self._validate_state_class(state_class)
        self._state_class = state_class


    @property
    def state_class(self) -> Type[Dict]:
        """Getter for the 'state_class' property."""
        return self._state_class

    @state_class.setter
    def state_class(self, value: Type[Dict]):
        """Setter for the 'state_class' property with validation."""
        self._validate_state_class(value)
        self._state_class = value


    @property
    def required_state_vars(self) -> List[str]:
        return self._required_state_vars

    @required_state_vars.setter
    def required_state_vars(self, value: List[str]):
        if not isinstance(value, list):
            raise TypeError("required_state_vars must be a list.")
        if not all(isinstance(item, str) for item in value):
            raise TypeError("All items in required_state_vars must be strings.")
        self._required_state_vars = value


    @abstractmethod
    def get_edge_function(self) -> Callable[[Dict[str, Any]], str]:
        """
        Returns the callable function for this conditional edge.
        
        The returned function should take a state dictionary and return
        a string that represents the next node to execute.
        """
        pass


    def _validate_state_class(self, state_class: Type[Dict]) -> None:
        """
        Validates that the state class contains the specific keys required for this edge.
        """
        if not all(key in state_class.__annotations__ for key in self._required_state_vars):
            raise AttributeError(
                f"The state class must have the following keys with Type hints: {self._required_state_vars}"
            )



class BaseAgenticConditionalEdge(BaseEdge):
    """
    Base abstract class for conditional edges that use an agent.
    
    This class handles agent validation and fallback logic, inheriting
    state validation from BaseEdge.
    """
    _agent_validation_Type: Literal['structured_output'] = 'structured_output'
    _output_property: Optional[str] = None

    def __init__(
        self,
        state_class: Type[Dict],
        required_state_vars: Optional[List[str]] = None,
        agent: Optional[BaseAgent] = None,
        output_property: Optional[str] = None
    ):
        """
        Initializes the agentic edge.
        
        Args:
            state_class: The TypedDict class representing the graph state.
            required_state_vars: An optional list of required state variables.
            agent: An optional pre-configured agent. If not provided, a default one is created.
            output_property: The name of the property expected in the agent's structured output.
        """
        super().__init__(
            state_class= state_class,
            required_state_vars= required_state_vars
        )
        
        self._output_property = output_property or self._output_property
        if self._output_property is None:
            raise TypeError("A specific output property must be provided or defined as a class attribute.")
        
        self._agent = agent or self.get_default_agent()
        self._validate_agent(self._agent)


    @property
    def agent(self) -> Optional[BaseAgent]:
        """Getter for the 'agent' property."""
        return self._agent

    @agent.setter
    def agent(self, value: BaseAgent):
        """Setter for the 'agent' property with validation."""
        self._validate_agent(value)
        self._agent = value


    @property
    def output_property(self) -> str:
        """Getter for the 'output_property' property."""
        return self._output_property

    @output_property.setter
    def output_property(self, value: str):
        """Setter for the 'output_property' property."""
        self._output_property = value


    @abstractmethod
    def get_default_agent(self) -> BaseAgent:
        """
        Provides the default agent instance for this specific edge.
        """
        pass


    def _validate_agent(self, agent: BaseAgent):
        """
        Validates the agent's structured output.
        """
        if not agent.structured_output:
            raise ValueError("The agent must have a structured output.")
        
        if self._output_property not in agent.structured_output.model_json_schema()['properties']:
            raise AttributeError(
                f"The structured output must have a '{self._output_property}' field."
            )



from abc import ABC, abstractmethod
import json
from typing import Any, Callable, Dict, List, Literal, Optional, Type

from ..agents import BaseAgent, BaseRetrievalAgent



class BaseNode(ABC):
    """
    A unified base class for all graph nodes, using dynamic agent validation.

    This class provides common functionality for nodes and infers agent validation
    based on a `_agent_validation_Type` class attribute in its subclasses.
    """
    
    _agent_validation_Type: Literal['structured_output', 'tools'] = None
    _required_state_vars: Optional[List[str]] = None
    _output_property: Optional[str] = None

    def __init__(
        self,
        state_class: Type[Dict],
        required_state_vars: Optional[List[str]] = None,
        agent: Optional[BaseAgent] = None,
        output_property: Optional[str] = None,
    ):
        """
        Initializes the base node.

        Args:
            state_class: The TypedDict class representing the graph state.
            required_state_vars: A list with the names of the state variables 
                    that are required for the node processing. Optional.
                    This list will be validated using `_validate_state_class` method.
            agent: An instance of a BaseAgent (or a subclass). Optional.
            output_property: The name of the property that is spected as output. Optional.
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


        self._output_property = output_property or self._output_property
        if output_property is not None and not isinstance(output_property, str):
            raise TypeError("output_property must be a string.")


        self._agent = agent or self.get_default_agent()
        if self._agent_validation_Type is not None and self._agent is not None:
            self._validate_agent(self._agent)
        elif self._agent_validation_Type is not None and self._agent is None:
            raise ValueError("An agent is required for this node Type but none was provided or a default could be found.")

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


    @property
    def output_property(self) -> str:
        return self._output_property

    @output_property.setter
    def output_property(self, value: str):
        if not isinstance(value, str):
            raise TypeError("output_property must be a string.")
        self._output_property = value


    @property
    def state_class(self) -> Type[Dict]:
        return self._state_class

    @state_class.setter
    def state_class(self, value: Type[Dict]):
        self._validate_state_class(value)
        self._state_class = value


    @property
    def agent(self) -> BaseAgent:
        return self._agent

    @agent.setter
    def agent(self, value: BaseAgent):
        self._validate_agent(value)
        self._agent = value


    @abstractmethod
    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Abstract method to return the callable node function.

        Each subclass must implement this method to define its specific node logic.
        """
        pass

    def get_default_agent(self) -> Optional[BaseAgent]:
        """
        Provides a default agent instance.
        Subclasses should override this method to return a specific default agent.
        """
        return None


    def _validate_agent(self, agent: BaseAgent):
        """
        Dynamically validates the agent based on the class's validation Type.
        """
        if self._agent_validation_Type == 'structured_output':
            if not agent.structured_output:
                raise ValueError("The agent must have a structured output.")

            self._validate_structured_output(agent)

        elif self._agent_validation_Type == 'tools':
            if not agent.tools:
                raise ValueError("The agent must have binded tools.")

        else:
            raise NotImplementedError(
                f"Agent validation Type '{self._agent_validation_Type}' is not supported."
            )


    def _validate_state_class(self, state_class: Type[Dict]):
        """
        Validates that the state class contains the specific keys required for this node.
        
        Args:
            state_class: The TypedDict class to validate.
            
        Raises:
            AttributeError: If the state class does not contain all required keys.
        """
        if not all(key in state_class.__annotations__ for key in self._required_state_vars):
            raise AttributeError(
                f"The state class must have the following keys with Type hints: {self._required_state_vars}"
            )


    def _validate_structured_output(self, agent: BaseAgent) -> None:
        """
        Validates the agent's structured output schema to ensure 
        it has the required field.
        
        Args:
            agent: The BaseAgent class to validate.
            
        Raises:
            AttributeError: If the agent does not contain the required output.
        """
        if self._output_property and self._output_property not in agent.structured_output.model_json_schema()['properties']:
            raise AttributeError(f"The structured output must have a '{self._output_property}' field.")



class BaseGenerateSubQueriesNode(BaseNode):
    """
    A generic base node for generating sub-queries for different entities.

    This abstract class handles the shared logic for creating relevant sub-queries,
    requiring subclasses to define the specific agent and entity name.
    """
    
    _agent_validation_Type = 'structured_output'
    _required_state_vars = ['user_query', 'entity', 'sub_queries', 'retieval_iterations']
    _output_property = 'queries'


    @property
    @abstractmethod
    def entity_name(self) -> str:
        """The name of the entity (e.g., 'mdl' or 'business_logic')."""
        pass


    def __init__(
        self,
        state_class: Type[Dict],
        agent: Optional[BaseRetrievalAgent] = None,
    ):
        """
        Initializes the node.

        Args:
            state_class: The TypedDict class representing the graph state.
            agent: The retrieval agent to use.
        """
        super().__init__(
            state_class= state_class,
            agent= agent,
        )

        if not hasattr(self.agent, 'max_subqueries'):
            raise TypeError("The agent must have a `max_subqueries` attribute.")


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.

        Returns:
            A function that takes the state dictionary and returns an updated state.
        """

        agent_runnable = self.agent.get_runnable()

        def generate_sub_queries(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Create relevant sub-queries for the user question to improve retrieval.

            Args:
                state: The current graph state.

            Returns:
                An updated state dictionary containing the generated sub-queries
                and updated retrieval iteration count.
            """
            print(f"--- GENERATING {self.entity_name.upper()} SUB-QUERIES 📚 ---")
            user_query = state['user_query']
            entity = state.get('entity', self.entity_name)
            retieval_iterations = state.get('retieval_iterations', 0)
            
            sub_queries = getattr(
                agent_runnable.invoke({'user_query': user_query}),
                self.output_property
            )

            return {
                'entity': entity,
                'sub_queries': sub_queries,
                'retieval_iterations': retieval_iterations + 1,
            }

        return generate_sub_queries



class BaseRetrieveToolNode(BaseNode):
    """
    A unified base class for graph nodes that retrieve information using a tool.
    
    This class handles the common logic for invoking a tool, inheriting all
    standard node behaviors from BaseNode.
    """

    _agent_validation_Type = None
    _output_property = None 

    _json_dumps: bool = False
    
    @property
    @abstractmethod
    def entity_name(self) -> str:
        """The name of the entity being retrieved (e.g., 'mdl' or 'business_logic')."""
        pass
    
    @property
    @abstractmethod
    def retrieval_result_key(self) -> str:
        """The specific key for the retrieval results in the graph state."""
        pass

    def __init__(
        self,
        tool: Callable,
        state_class: Type[Dict],
    ):
        """
        Initializes the base retrieval node.

        Args:
            tool: The LangChain tool or any callable to be invoked for retrieval.
            state_class: The TypedDict class used for the graph state.
        
        Raises:
            TypeError: If the provided tool is not callable.
        """
        if not isinstance(tool, Callable):
            raise TypeError("'tool' must be a callable object.")
        self._tool = tool

        required_state_vars = ['sub_queries', 'retrieval_results', self.retrieval_result_key]
        
        super().__init__(
            state_class= state_class,
            required_state_vars= required_state_vars,
            agent= None,
            output_property= self._output_property
        )

    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.
        
        This method is now a concrete implementation, providing the common
        retrieval logic for all subclasses.
        """
        def retrieve_queries(state: Dict[str, Any]) -> Dict[str, Any]:
            print(f"--- {self.entity_name.upper()} RETRIEVE TOOL 🛠️ ---")
            queries = state['sub_queries']
            
            retrieval_results = self._tool.invoke({'queries': queries})

            if self._json_dumps:
                formatted_results = [
                    json.dumps(result, indent=2, ensure_ascii=False)
                    for result in retrieval_results
                ]
            else:
                formatted_results = retrieval_results

            return {
                'retrieval_results': formatted_results,
                self.retrieval_result_key: retrieval_results
            }
            
        return retrieve_queries



class BaseMultiOutputAgentNode(BaseNode):
    """
    A unified base class for graph nodes that produce multiple outputs from an agent.

    This class serves as a blueprint for nodes that require a structured agent 
    output with multiple fields. It is an **abstract class** and cannot be 
    instantiated directly. Instead, concrete node classes should inherit from it, 
    define their specific `_required_state_vars` and `_output_properties`, and 
    implement the `get_node_function` method to handle the specific logic of the node.
    
    This design ensures that any multi-output agent node adheres to the same 
    validation and property-handling contract, promoting consistency across the 
    system.
    """

    _agent_validation_Type = 'structured_output'
    _output_properties: List[str] = None

    def __init__(
        self,
        state_class: Type[Dict],
        output_properties: List[str],
        required_state_vars: Optional[List[str]] = None,
        agent: Optional[BaseAgent] = None,
    ):
        """
        Initializes the multi-output agent node.

        Args:
            state_class: The TypedDict class representing the graph state.
            required_state_vars: A list with the names of the state variables that are
                    required for the node's processing. It must include
                    all `output_properties`.
            agent: An instance of a BaseAgent. This agent must have a structured
                    output defined.
            output_properties: A list of strings with the names of the properties
                    expected in the agent's structured output. This list
                    is required for multi-output nodes.
        
        Raises:
            ValueError: If `output_properties` is not a non-empty list.
            ValueError: If any property in `output_properties` is not included
                    in `required_state_vars`.
        """
        
        if output_properties is None or not isinstance(output_properties, list) or not output_properties:
            raise ValueError("A list of 'output_properties' is required for a multi-output node.")
        self._output_properties = output_properties


        if not required_state_vars:
            required_state_vars = self._output_properties
        else:
            if not all(prop in required_state_vars for prop in self._output_properties):
                raise ValueError("All 'output_properties' must be included in the 'required_state_vars' list.")
            
        super().__init__(
            state_class= state_class,
            required_state_vars= required_state_vars,
            agent= agent,
            output_property= None
        )


    @property
    def output_properties(self) -> List[str]:
        """
        Returns the list of expected output properties.
        """
        return self._output_properties

    @output_properties.setter
    def output_properties(self, value: List[str]):
        """
        Sets the list of expected output properties with validation.
        """
        if not isinstance(value, list):
            raise TypeError("output_properties must be a list.")
        if not all(isinstance(item, str) for item in value):
            raise TypeError("All items in output_properties must be strings.")
        self._output_properties = value


    @property
    def required_state_vars(self) -> List[str]:
        return self._required_state_vars

    @required_state_vars.setter
    def required_state_vars(self, value: List[str]):
        if not isinstance(value, list):
            raise TypeError("required_state_vars must be a list.")
        if not all(isinstance(item, str) for item in value):
            raise TypeError("All items in required_state_vars must be strings.")
        
        # CHANGE: Add validation that the output properties are a subset of the required state vars.
        if self._output_properties and not all(prop in value for prop in self._output_properties):
            raise ValueError("All output_properties must be included in the required_state_vars list.")
        
        self._required_state_vars = value
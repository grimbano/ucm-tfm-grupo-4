
from typing import Any, Callable, Dict, List, Optional, Type

from .base import BaseMultiOutputAgentNode
from ..agents import BaseAgent, DbSchemaExtractor



class ExtractDbSchemaNode(BaseMultiOutputAgentNode):
    """
    A node that extracts the DB and Schema names from the data schema summary.
    
    This node inherits from `BaseMultiOutputAgentNode` to handle the extraction
    of multiple properties (`db_name` and `schema_name`) from a structured agent
    response.
    """

    _agent_validation_Type = 'structured_output'
    _required_state_vars = ['data_schema', 'db_name', 'schema_name']
    _output_properties = ['db_name', 'schema_name']

    def __init__(
        self,
        state_class: Type[Dict],
        required_state_vars: Optional[List[str]] = None,
        agent: Optional[BaseAgent] = None,
        output_properties: Optional[List[str]] = None
    ):
        """
        Initializes the DefineUserQueryLanguageNode instance.

        Args:
            state_class: The TypedDict class representing the graph state.
            required_state_vars: A list with the names of the state variables that are
                    required for the node processing. Defaults to the
                    class attribute `_required_state_vars`.
            agent: The instance of the DbSchemaExtractor agent to use for the
                    extraction task. Defaults to a new instance of `DbSchemaExtractor`.
            output_properties: A list with the names of the properties that are expected
                    as output. Defaults to the class attribute `_output_properties`.
        """
        super().__init__(
            state_class= state_class,
            required_state_vars= required_state_vars,
            agent= agent,
            output_properties= output_properties or self._output_properties
        )


    def get_default_agent(self) -> DbSchemaExtractor:
        """
        Provides a new default DB and Schema names extractor agent for this node.
        
        Returns:
            A new instance of DbSchemaExtractor.
        """
        return DbSchemaExtractor()


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.
        
        This method is now a concrete implementation, providing the specific logic
        for extracting data using the agent.
        
        Returns:
            A function that takes the state dictionary and returns an updated state.
        """
        agent_runnable = self.agent.get_runnable()

        def extract_db_schema_node(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Extract the DB and schema names from the data schema summary.

            Args:
                state: The current graph state.

            Returns:
                An updated state dictionary containing the db_name and schema_name.
            """
            print("--- EXTRACT DB SCHEMA 🧮 ---")
            
            data_schema = state['data_schema']
            
            agent_response = agent_runnable.invoke({'data_schema': data_schema})

            return {
                prop: getattr(agent_response, prop)
                for prop in self.output_properties
            }

        return extract_db_schema_node
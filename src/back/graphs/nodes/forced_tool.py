
from typing import Callable, Dict, Type

from .base import BaseRetrieveToolNode



class RetrieveBusinessLogicQueriesNode(BaseRetrieveToolNode):
    """
    A node that retrieves business logic results using a dedicated tool.
    
    This class inherits the core retrieval and validation logic from BaseRetrieveToolNode.
    """

    entity_name = 'business_logic'
    retrieval_result_key = 'business_logic_retrieval_results'
    _json_dumps = False

    def __init__(
        self,
        retriever_tool: Callable,
        state_class: Type[Dict]
    ):
        """
        Initializes the node with the business logic tool and the graph state class.

        Args:
            retriever_tool: A callable tool that retrieves business logic information.
            state_class: The TypedDict class representing the graph state.
        """
        super().__init__(
            tool= retriever_tool, 
            state_class= state_class
        )


class RetrieveMdlQueriesNode(BaseRetrieveToolNode):
    """
    A node that retrieves MDL data schema results using a dedicated tool.
    
    This class inherits the core retrieval logic from BaseRetrieveToolNode,
    enabling JSON serialization via the _json_dumps class variable.
    """

    entity_name = 'mdl'
    retrieval_result_key = 'mdl_retrieval_results'
    _json_dumps = True

    def __init__(
        self, 
        retriever_tool: Callable,
        state_class: Type[Dict]
    ):
        """
        Initializes the node with the MDL data tool and the graph state class.

        Args:
            retriever_tool: A callable tool that retrieves MDL data.
            state_class: The TypedDict class representing the graph state.
        """
        super().__init__(
            tool= retriever_tool,
            state_class= state_class
        )


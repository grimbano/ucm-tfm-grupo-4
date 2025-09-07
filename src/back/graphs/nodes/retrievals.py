
from .base import BaseGenerateSubQueriesNode
from ..agents import (
    BusinessLogicRetriever,
    MdlRetriever
)


class GenerateBusinessLogicSubQueriesNode(BaseGenerateSubQueriesNode):
    """
    A node that generates sub-queries for business logic retrieval.
    """

    entity_name = 'business_logic'

    def get_default_agent(self) -> BusinessLogicRetriever:
        """
        Provides a new default retrieval business logic agent for this node.
        
        Returns:
            A new instance of BusinessLogicRetriever.
        """
        return BusinessLogicRetriever()


class GenerateMdlSubQueriesNode(BaseGenerateSubQueriesNode):
    """
    A node that generates sub-queries for MDL schema retrieval.
    """

    entity_name = 'mdl'

    def get_default_agent(self) -> MdlRetriever:
        """
        Provides a new default retrieval MDL agent for this node.
        
        Returns:
            A new instance of MdlRetriever.
        """
        return MdlRetriever()



from typing import Optional
from langchain_core.language_models import BaseChatModel

from .base import BaseRetrievalAgent
from ..prompts import BusinessLogicRetrieverPrompt, MdlRetrieverPrompt



class BusinessLogicRetriever(BaseRetrievalAgent):
    """
    An agent specialized for retrieving business logic and rules from a knowledge base.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
        max_subqueries: Optional[int] = None,
    ):
        """
        Initializes the business logic retriever agent.

        Args:
            llm: The LangChain chat model to be used. 
                    Defaults to a predefined retrieval model.
            system_prompt: The system message for the prompt constructor. 
                    Defaults to a predefined message.
            human_message: The human message for the prompt constructor. 
                    Defaults to a predefined message.
            max_subqueries: The maximum number of sub-queries to generate.
                    Defaults to a predefined value in BaseRetrievalAgent.
        """
        super().__init__(
            llm= llm,
            prompt_constructor= BusinessLogicRetrieverPrompt(
                system_prompt= system_prompt,
                human_message= human_message,
                max_subqueries= max_subqueries,
            ),
            max_subqueries= max_subqueries,
        )


class MdlRetriever(BaseRetrievalAgent):
    """
    An agent specialized for retrieving information from a Model Definition Language (MDL) document.

    This class extends `BaseRetrievalAgent` to perform MDL-specific retrieval tasks. It uses
    a dedicated LLM and a prompt to generate search queries, and inherits the logic for
    dynamically creating a structured output schema based on a maximum number of sub-queries.
    """

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
        max_subqueries: Optional[int] = None,
    ):
        """
        Initializes the MDL retriever agent.

        Args:
            llm: The LangChain chat model to be used.
                Defaults to a predefined retrieval model.
            system_prompt: The system message for the prompt constructor.
                    Defaults to a predefined message.
            human_message: The human message for the prompt constructor.
                    Defaults to a predefined message.
            max_subqueries: The maximum number of sub-queries to generate.
                    Defaults to a predefined value in BaseRetrievalAgent.
        """
        super().__init__(
            llm= llm,
            prompt_constructor= MdlRetrieverPrompt(
                system_prompt= system_prompt,
                human_message= human_message,
                max_subqueries= max_subqueries,
            ),
            max_subqueries= max_subqueries,
        )


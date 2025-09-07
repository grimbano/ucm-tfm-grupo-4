
from typing import Optional

from .base import BasePrompt
from .templates import (
    _user_query_human_message,
    _business_logic_retrieval_system_prompt,
    _mdl_retrieval_system_prompt,
)



class BusinessLogicRetrieverPrompt(BasePrompt):
    """
    A specific prompt implementation for a business logic retriever.

    This class encapsulates the predefined system and human messages necessary
    to guide a large language model (LLM) in retrieving business rules. It 
    provides sensible defaults but also allows for custom messages to be provided 
    during initialization.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
        max_subqueries: Optional[int] = None,
    ):
        """
        Initializes the BusinessLogicRetrieverPrompt with default or custom messages.

        Args:
            system_prompt: The system message that instructs the model on
                    how to act as a retriever of business logic.
                    Defaults to a predefined message if not provided.
            human_message: The human message template that contains the user's query.
                    Defaults to a predefined message if not provided.
            max_subqueries: The maximum number of sub-queries to generate. Used
                    to format the default system prompt. Defaults to a
                    predefined value.
        """
        if system_prompt is None:
            _system_prompt = _business_logic_retrieval_system_prompt.format(
                max_subqueries= max_subqueries or 5
            )
        else:
            _system_prompt = system_prompt

        super().__init__(
            system_prompt= _system_prompt,
            human_message= human_message or _user_query_human_message
        )



class MdlRetrieverPrompt(BasePrompt):
    """
    A specific prompt implementation for a MDL data schema retriever.

    This class encapsulates the predefined system and human messages necessary
    to guide a large language model (LLM) in retrieving MDL data schema. It 
    provides sensible defaults but also allows for custom messages to be provided 
    during initialization.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
        max_subqueries: Optional[int] = None,
    ):
        """
        Initializes the MdlRetrieverPrompt with default or custom messages.

        Args:
            system_prompt: The system message that instructs the model on
                    how to act as a retriever of MDL data schema.
                    Defaults to a predefined message if not provided.
            human_message: The human message template that contains the user's query.
                    Defaults to a predefined message if not provided.
            max_subqueries: The maximum number of sub-queries to generate. Used
                    to format the default system prompt. Defaults to a
                    predefined value.
        """

        if system_prompt is None:
            _system_prompt = _mdl_retrieval_system_prompt.format(
                max_subqueries=max_subqueries or 5
            )
        else:
            _system_prompt = system_prompt

        super().__init__(
            system_prompt= _system_prompt,
            human_message= human_message or _user_query_human_message
        )


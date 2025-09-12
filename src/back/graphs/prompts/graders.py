
from typing import Optional

from .base import BasePrompt
from .templates import (
    _user_query_human_message,
    _business_relevance_grader_system_prompt,
    _retrieval_grader_system_prompt,
    _retrieval_grader_human_message,
    _hallucination_grader_system_prompt,
    _hallucination_grader_human_message,
    _answer_grader_system_prompt,
    _answer_grader_human_message,
    _global_retrieval_grader_system_prompt,
)


class BusinessRelevanceGraderPrompt(BasePrompt):
    """
    A specific implementation of a prompt for a business relevance topic grader.

    This class encapsulates the system and human messages required to grade
    the relevance of an user's query for a business context. It uses
    properties for easy access and modification of the prompt components.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
    ):
        """
        Initializes the BusinessRelevanceGraderPrompt with default or custom messages.

        Args:
            system_prompt: The system message for the grader.
                    Defaults to a predefined message if not provided.
            human_message: The human message template for the grader.
                    Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _business_relevance_grader_system_prompt,
            human_message= human_message or _user_query_human_message
        )


class RetrievalGraderPrompt(BasePrompt):
    """
    A specific implementation of a prompt for a retrieval grader.

    This class encapsulates the system and human messages required to grade
    the relevance of a retrieved document against an user's query. It uses
    properties for easy access and modification of the prompt components.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
    ):
        """
        Initializes the RetrievalGraderPrompt with default or custom messages.

        Args:
            system_prompt: The system message for the grader.
                    Defaults to a predefined message if not provided.
            human_message: The human message template for the grader.
                    Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _retrieval_grader_system_prompt,
            human_message= human_message or _retrieval_grader_human_message
        )



class HallucinationGraderPrompt(BasePrompt):
    """
    A specific implementation of a prompt for a hallucination grader.

    This class encapsulates the system and human messages required to grade
    a generated answer for factual correctness against a retrieved document.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
    ):
        """
        Initializes the HallucinationGraderPrompt with default or custom messages.

        Args:
            system_prompt: The system message for the grader.
                    Defaults to a predefined message if not provided.
            human_message: The human message template for the grader.
                    Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _hallucination_grader_system_prompt,
            human_message= human_message or _hallucination_grader_human_message
        )



class AnswerGraderPrompt(BasePrompt):
    """
    A specific implementation of a prompt for an answer grader.

    This class provides default system and human messages for 
    evaluating the relevance and factual basis of a generated answer.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
    ):
        """
        Initializes the AnswerGraderPrompt with default or custom messages.

        Args:
            system_prompt: The system message for the grader.
                    Defaults to a predefined message if not provided.
            human_message: The human message template for the grader.
                    Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _answer_grader_system_prompt,
            human_message= human_message or _answer_grader_human_message
        )



class GlobalRetrievalGraderPrompt(BasePrompt):
    """
    A specific implementation of a prompt for a business context grader.

    This class encapsulates the system and human messages required to grade
    the relevance of a global business context summary against a user's query. 
    It uses properties for easy access and modification of the prompt components.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
    ):
        """
        Initializes the GlobalRetrievalGraderPrompt with default or custom messages.

        Args:
            system_prompt: The system message for the grader.
                    Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _global_retrieval_grader_system_prompt,
        )


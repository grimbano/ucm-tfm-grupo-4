
from typing import Dict, Optional, Type, Union
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel


from .base import BaseAgent
from ..models import llm_graders
from ..prompts import (
    GlobalRetrievalGraderPrompt,
    RetrievalGraderPrompt,
    HallucinationGraderPrompt,
    AnswerGraderPrompt,
)
from ..pydantic_models import (
    RetrievalGraderResult,
    GlobalRetrievalGraderResult,
    HallucinationGraderResult,
    AnswerGraderResult,
)



class RetrievalGrader(BaseAgent):
    """
    An agent for grading the relevance of retrieved documents against a user's query.

    This class specializes `BaseAgent` with a default LLM, a dedicated prompt constructor,
    and a structured output schema to determine if a retrieved document is relevant
    to the given question.
    """

    _default_llm = llm_graders
    _default_structured_output = RetrievalGraderResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the retrieval grader agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined classifier model.
            system_prompt: The system message. Defaults to a predefined message.
            human_message: The human message. Defaults to a predefined message.
            structured_output: The output schema. Defaults to a predefined result schema.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= RetrievalGraderPrompt(
                system_prompt= system_prompt,
                human_message= human_message,
            ),
            structured_output= structured_output or self._default_structured_output
        )



class HallucinationGrader(BaseAgent):
    """
    An agent for grading a generated answer for hallucinations against its source documents.

    This class specializes `BaseAgent` with a default LLM, a dedicated prompt constructor,
    and a structured output schema to determine if the generated answer is supported
    by the provided context.
    """

    _default_llm = llm_graders
    _default_structured_output = HallucinationGraderResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the hallucination grader agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined classifier model.
            system_prompt: The system message. Defaults to a predefined message.
            human_message: The human message. Defaults to a predefined message.
            structured_output: The output schema. Defaults to a predefined result schema.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= HallucinationGraderPrompt(
                system_prompt= system_prompt,
                human_message= human_message,
            ),
            structured_output= structured_output or self._default_structured_output
        )



class AnswerGrader(BaseAgent):
    """
    An agent for grading whether a generated answer is relevant to a user's question.

    This class specializes `BaseAgent` with a default LLM, a dedicated prompt constructor,
    and a structured output schema to assess the relevance of the final answer
    to the original query.
    """

    _default_llm = llm_graders
    _default_structured_output = AnswerGraderResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the answer grader agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined classifier model.
            system_prompt: The system message. Defaults to a predefined message.
            human_message: The human message. Defaults to a predefined message.
            structured_output: The output schema. Defaults to a predefined result schema.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= AnswerGraderPrompt(
                system_prompt= system_prompt,
                human_message= human_message,
            ),
            structured_output= structured_output or self._default_structured_output
        )



class GlobalRetrievalGrader(BaseAgent):
    """
    An agent for grading the relevance of global business context against a user's query.

    This class specializes `BaseAgent` with a default LLM, a dedicated prompt constructor,
    and a structured output schema to determine if a bringed context is relevant
    to the given question.
    """

    _default_llm = llm_graders
    _default_structured_output = GlobalRetrievalGraderResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the retrieval grader agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined classifier model.
            system_prompt: The system message. Defaults to a predefined message.
            structured_output: The output schema. Defaults to a predefined result schema.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= GlobalRetrievalGraderPrompt(
                system_prompt= system_prompt,
            ),
            structured_output= structured_output or self._default_structured_output
        )


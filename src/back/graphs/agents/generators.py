
from typing import Dict, Optional, Type, Union
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel

from .base import BaseAgent
from ..models import llm_generators
from ..prompts import (
    ChunkSummaryGeneratorPrompt,
    BusinessLogicSummarizerPrompt,
    MdlSummarizerPrompt,
    GlobalContextGeneratorPrompt,
    NoRelevantContextGeneratorPrompt,
)
from ..pydantic_models import (
    ChunkSummaryGeneratorResult,
    BusinessLogicSummarizerResult,
    MdlSummarizerResult,
    GlobalContextGeneratorResult,
    NoRelevantContextGeneratorResult,
)



class ChunkSummaryGenerator(BaseAgent):
    """
    An agent for generating concise summaries of document chunks.

    This class specializes `BaseAgent` with a default LLM, a prompt constructor
    for chunk summaries, and a structured output schema to ensure the summary
    is returned in a consistent format.
    """

    _default_llm = llm_generators
    _default_structured_output = ChunkSummaryGeneratorResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the chunk summary generator agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined model.
            system_prompt: The system message. Defaults to a predefined message.
            structured_output: The schema for the output. Defaults to a predefined
                    result schema for chunk summaries.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= ChunkSummaryGeneratorPrompt(
                system_prompt= system_prompt,
            ),
            structured_output= structured_output or self._default_structured_output
        )



class BusinessLogicSummarizer(BaseAgent):
    """
    An agent for summarizing retrieved business logic and rules.

    This class specializes `BaseAgent` to handle business-specific summarization tasks
    by using a dedicated prompt and a structured output schema for the results.
    """

    _default_llm = llm_generators
    _default_structured_output = BusinessLogicSummarizerResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the business logic summarizer agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined model.
            system_prompt: The system message. Defaults to a predefined message.
            structured_output: The schema for the output. Defaults to a predefined
                    result schema for business logic summaries.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= BusinessLogicSummarizerPrompt(
                system_prompt= system_prompt,
            ),
            structured_output= structured_output or self._default_structured_output
        )



class MdlSummarizer(BaseAgent):
    """
    An agent for summarizing documents in Model Definition Language (MDL).

    This class specializes `BaseAgent` to process and summarize MDL content, using
    a specific prompt and output schema tailored for the task.
    """

    _default_llm = llm_generators
    _default_structured_output = MdlSummarizerResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the MDL summarizer agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined model.
            system_prompt: The system message. Defaults to a predefined message.
            structured_output: The schema for the output. Defaults to a predefined
                    result schema for MDL summaries.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= MdlSummarizerPrompt(
                system_prompt= system_prompt,
            ),
            structured_output= structured_output or self._default_structured_output
        )



class GlobalContextGenerator(BaseAgent):
    """
    An agent for generating a global context from multiple information sources.

    This class specializes `BaseAgent` to synthesize and consolidate a comprehensive
    global context using a dedicated prompt and structured output schema.
    """

    _default_llm = llm_generators
    _default_structured_output = GlobalContextGeneratorResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the global context generator agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined model.
            system_prompt: The system message. Defaults to a predefined message.
            structured_output: The schema for the output. Defaults to a predefined
                    result schema for global context generation.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= GlobalContextGeneratorPrompt(
                system_prompt= system_prompt,
            ),
            structured_output= structured_output or self._default_structured_output
        )



class NoRelevantContextGenerator(BaseAgent):
    """
    An agent for generating a response when no relevant context is found.

    This class specializes `BaseAgent` to provide a standardized, polite response
    for situations where a search or retrieval process yields no results.
    """

    _default_llm = llm_generators
    _default_structured_output = NoRelevantContextGeneratorResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the no-relevant-context generator agent.

        Args:
            llm: The LangChain chat model. Defaults to a predefined model.
            system_prompt: The system message. Defaults to a predefined message.
            structured_output: The schema for the output. Defaults to a predefined
                    result schema for generating no-context responses.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= NoRelevantContextGeneratorPrompt(
                system_prompt= system_prompt,
            ),
            structured_output= structured_output or self._default_structured_output
        )


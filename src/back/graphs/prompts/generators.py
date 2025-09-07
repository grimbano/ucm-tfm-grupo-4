
from typing import Optional

from .base import BasePrompt
from .templates import (
    _chunk_summary_generator_system_prompt,
    _business_logic_summarizer_system_prompt,
    _mdl_summarizer_system_prompt,
    _global_context_generator_system_prompt,
    _no_relevant_context_generator_system_prompt,
)


class ChunkSummaryGeneratorPrompt(BasePrompt):
    """
    A specific prompt implementation for generating summaries of document chunks.

    This class provides a default system message to guide a large language model
    (LLM) in creating concise and effective summaries of text chunks.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
    ):
        """
        Initializes the ChunkSummaryGeneratorPrompt with a default or custom system message.

        Args:
            system_prompt: The system message that instructs the model
                    on how to generate a chunk summary. Defaults to a predefined message
                    if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _chunk_summary_generator_system_prompt
        )



class BusinessLogicSummarizerPrompt(BasePrompt):
    """
    A specific prompt implementation for summarizing retrieved business logic.

    This class provides a default system message to instruct a large language model 
    (LLM) on how to act as a summarizer of business rules and data schemas. 
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
    ):
        """
        Initializes the BusinessLogicSummarizerPrompt with a default or custom system message.

        Args:
            system_prompt: The system message that instructs the model on how to summarize 
                    business logic. Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _business_logic_summarizer_system_prompt
        )



class MdlSummarizerPrompt(BasePrompt):
    """
    A specific prompt implementation for summarizing a model definition language (MDL) document.

    This class provides a default system message to guide a large language model (LLM) on how to 
    summarize MDL documents, which are often used to describe data models or business logic.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
    ):
        """
        Initializes the MdlSummarizerPrompt with a default or custom system message.

        Args:
            system_prompt: The system message that instructs the model on how to summarize MDL documents.
                    Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _mdl_summarizer_system_prompt
        )



class GlobalContextGeneratorPrompt(BasePrompt):
    """
    A specific prompt implementation for generating a global context from multiple sources.

    This class provides a default system message to guide a large language model (LLM) on how to 
    synthesize a cohesive and comprehensive global context from various pieces of retrieved information.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
    ):
        """
        Initializes the GlobalContextGeneratorPrompt with a default or custom system message.

        Args:
            system_prompt: The system message that instructs the model on how to generate a global context.
                    Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _global_context_generator_system_prompt
        )



class NoRelevantContextGeneratorPrompt(BasePrompt):
    """
    A specific prompt implementation for handling cases where no relevant context is found.

    This class provides a default system message to guide a large language model (LLM) on how to
    construct an appropriate response when the retrieval process fails to find any useful information
    related to the user's query.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
    ):
        """
        Initializes the NoRelevantContextGeneratorPrompt with a default or custom system message.

        Args:
            system_prompt: The system message that instructs the model on how to respond
                    when no relevant context is available.
                    Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _no_relevant_context_generator_system_prompt
        )



from typing import Dict, Optional, Type, Union
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel

from .base import BaseAgent
from ..models import llm_retrievals
from ..prompts import DbSchemaExtractorPrompt
from ..pydantic_models import DbSchemaExtractionResult



class DbSchemaExtractor(BaseAgent):
    """
    An agent designed to extract database and schema names from a given text.

    This agent uses a large language model (LLM) and a structured output schema
    to accurately identify and extract specific data parameters from a descriptive
    text, such as a summary of a data schema. It is built to be a robust, single-
    purpose extraction tool that can be easily integrated into larger data processing
    pipelines.
    """

    _default_llm = llm_retrievals
    _default_structured_output = DbSchemaExtractionResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the LanguageClassifier agent.

        Args:
            llm: The LangChain chat model to be used. Defaults to a predefined
                    retrievals LLM if not provided.
            system_prompt: The system message for the prompt constructor. Defaults to
                    a predefined message if not provided.
            structured_output: The schema that defines the expected output structure.
                    Defaults to a predefined result schema for DB Schema extraction.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= DbSchemaExtractorPrompt(
                system_prompt= system_prompt,
            ),
            structured_output= structured_output or self._default_structured_output
        )


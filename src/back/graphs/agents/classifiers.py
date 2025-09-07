
from typing import Dict, Optional, Type, Union
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel

from .base import BaseAgent
from ..models import llm_classifiers
from ..prompts import LanguageClassifierPrompt
from ..pydantic_models import LanguageClassifierResult



class LanguageClassifier(BaseAgent):
    """
    A specific agent implementation for classifying the language of a text.

    This class specializes the `BaseAgent` by providing default values for its
    LLM, prompt constructor, and structured output schema, making it ready-to-use
    for language classification tasks out of the box.
    """

    _default_llm = llm_classifiers
    _default_structured_output = LanguageClassifierResult

    def __init__(
        self,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
    ):
        """
        Initializes the LanguageClassifier agent.

        Args:
            llm: The LangChain chat model to be used. Defaults to a predefined
                    classifier LLM if not provided.
            system_prompt: The system message for the prompt constructor. Defaults to
                    a predefined message if not provided.
            human_message: The human message for the prompt constructor. Defaults to
                    a predefined message if not provided.
            structured_output: The schema that defines the expected output structure.
                    Defaults to a predefined result schema for language classification
                    if not provided.
        """
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= LanguageClassifierPrompt(
                system_prompt= system_prompt,
                human_message= human_message,
            ),
            structured_output= structured_output or self._default_structured_output
        )



from typing import Optional

from .base import BasePrompt
from .templates import (
    _user_query_human_message,
    _language_classifier_system_prompt,
)



class LanguageClassifierPrompt(BasePrompt):
    """
    A specific prompt implementation for a language classifier.

    This class provides default system and human messages to guide a large language
    model (LLM) in determining the language of a given text.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
        human_message: Optional[str] = None,
    ):
        """
        Initializes the LanguageClassifierPrompt with default or custom messages.

        Args:
            system_prompt: The system message that instructs the model on how to
                    classify the language of a text. Defaults to a predefined
                    message if not provided.
            human_message: The human message template that contains the text to be
                    classified. Defaults to a predefined message if not provided.
        """
        super().__init__(
            system_prompt= system_prompt or _language_classifier_system_prompt,
            human_message= human_message or _user_query_human_message
        )


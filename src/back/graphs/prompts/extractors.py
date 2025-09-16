
from typing import Optional

from .base import BasePrompt
from .templates import (
    _db_schema_extractor_prompt,
)



class DbSchemaExtractorPrompt(BasePrompt):
    """
    A prompt class specifically designed to extract database and 
    schema parameters from a text context.

    This class provides a predefined system prompt to instruct a 
    language model on how to perform the extraction task.
    """

    def __init__(
        self,
        system_prompt: Optional[str] = None,
    ):
        """
        Initializes the DbParamsExtractorPrompt with default or custom messages.

        Args:
            system_prompt: An optional custom system prompt.
                If not provided, it defaults to the
                `_db_params_extractor_prompt` constant.
        """
        super().__init__(
            system_prompt= system_prompt or _db_schema_extractor_prompt,
        )




from typing import Optional
from langchain.prompts import ChatPromptTemplate



class BasePrompt:
    """
    A base class for encapsulating system and optional human messages for a prompt.

    This class serves as a fundamental building block for creating prompts,
    enforcing that a system message is provided at initialization. It provides
    properties for controlled access and modification of the messages, and a
    callable interface to generate a LangChain `ChatPromptTemplate`.
    """

    def __init__(
        self,
        system_prompt: str,
        human_message: Optional[str] = None,
    ):
        """
        Initializes the prompt with a system message and an optional human message.

        This constructor requires a system prompt. The human message is optional.

        Args:
            system_prompt: The system message that defines the AI's role.
            human_message: The human message template. Defaults to None.
        
        Raises:
            ValueError: If `system_prompt` is empty or not provided.
        """
        if system_prompt is None or not isinstance(system_prompt, str):
            raise TypeError("A 'system_prompt' must be specified and must be a string.")
        
        if human_message is not None and not isinstance(human_message, str):
            raise TypeError("Human message must be a string or None.")
            
        self._system_prompt = system_prompt
        self._human_message = human_message


    @property
    def system_prompt(self) -> str:
        """The system prompt."""
        return self._system_prompt

    @system_prompt.setter
    def system_prompt(self, value: str):
        """Sets the system prompt."""
        if value is None or not isinstance(value, str):
            raise TypeError("A 'system_prompt' must be specified and must be a string.")
        self._system_prompt = value


    @property
    def human_message(self) -> Optional[str]:
        """The human message template."""
        return self._human_message

    @human_message.setter
    def human_message(self, value: Optional[str]):
        """Sets the human message template."""
        if value is not None and not isinstance(value, str):
            raise TypeError("Human message must be a string or None.")
        self._human_message = value


    def __call__(self) -> ChatPromptTemplate:
        """
        Generates and returns a ChatPromptTemplate.
        
        It includes the human message if one is present.
        """
        messages = [('system', self.system_prompt)]
        if self.human_message is not None:
            messages.append(('human', self.human_message))
        
        return ChatPromptTemplate.from_messages(messages)



from typing import Dict, Optional, Sequence, Type, Union
from pydantic import BaseModel
from langchain_core.language_models import BaseChatModel
from langchain_core.runnables import RunnableSequence
from langchain.tools import BaseTool

from ..prompts import BasePrompt
from ..models import llm_retrievals
from ..pydantic_models import create_retriever_input_class



class BaseAgent:
    """
    A base class for agents that use prompts and an LLM to generate output.

    This class encapsulates a Large Language Model (LLM), a structured output schema,
    and a prompt constructor. It is designed to work with a unified prompt class
    that can handle both system-only and system-and-human prompts.
    """

    def __init__(
        self,
        llm: BaseChatModel,
        prompt_constructor: BasePrompt,
        structured_output: Optional[Union[BaseModel, Dict, Type]] = None,
        tools: Optional[Sequence[BaseTool]] = None,
    ):
        """
        Initializes the agent with the necessary components.

        Args:
            llm: The LangChain chat model to be used.
            prompt_constructor: An instance of the unified prompt class.
            structured_output: The schema (Pydantic model, dictionary, etc.) that defines the
                    expected output structure from the LLM. It is optional.
            tools: A sequence of tools to be bound to the LLM. It is optional.
        
        Raises:
            ValueError: If both `structured_output` and `tools` are provided simultaneously.
            TypeError: If `llm` is not an instance of LangChain BaseChatModel.
        """
        if structured_output is not None and tools is not None:
            raise ValueError(
                "Cannot pass both 'structured_output' and 'tools' simultaneously."
            )
        
        if not isinstance(llm, BaseChatModel):
            raise TypeError("llm must be an instance of BaseChatModel.")

        self._llm = llm
        self._prompt_constructor = prompt_constructor
        self._structured_output = structured_output
        self._tools = tools


    @property
    def llm(self) -> BaseChatModel:
        """Gets the LangChain chat model instance."""
        return self._llm

    @llm.setter
    def llm(self, value: BaseChatModel):
        """Sets the LangChain chat model instance."""
        if not isinstance(value, BaseChatModel):
            raise TypeError("llm must be an instance of BaseChatModel.")
        self._llm = value


    @property
    def prompt_constructor(self) -> BasePrompt:
        """Gets the prompt constructor instance."""
        return self._prompt_constructor

    @prompt_constructor.setter
    def prompt_constructor(self, value: BasePrompt):
        """Sets the prompt constructor instance."""
        self._prompt_constructor = value


    @property
    def structured_output(self) -> Optional[Union[BaseModel, Dict, Type]]:
        """Gets the structured output schema."""
        return self._structured_output

    @structured_output.setter
    def structured_output(self, value: Optional[Union[BaseModel, Dict, Type]]):
        """Sets the structured output schema."""
        self._structured_output = value


    @property
    def tools(self) -> Optional[Sequence[BaseTool]]:
        """Gets the sequence of tools."""
        return self._tools

    @tools.setter
    def tools(self, value: Optional[Sequence[BaseTool]]):
        """Sets the sequence of tools."""
        self._tools = value


    def get_runnable(self) -> RunnableSequence:
        """
        Creates and returns a LangChain runnable.

        The runnable chains the prompt, the LLM, and either a structured output parser or tool binding.
        """
        if self._structured_output is not None:
            llm_chain = self._llm.with_structured_output(self._structured_output)

        elif self._tools is not None:
            llm_chain = self._llm.bind_tools(self._tools)

        else:
            llm_chain = self._llm
        

        return self._prompt_constructor() | llm_chain



class BaseRetrievalAgent(BaseAgent):
    """
    A base class for agents specialized in generating retrieval queries.

    This class provides core functionality for agents that need to dynamically
    create a structured output schema based on a maximum number of subqueries.
    It enforces mutual exclusivity between the `max_subqueries` and `structured_output`
    parameters, ensuring a consistent and predictable state.
    """

    _default_llm = llm_retrievals
    _default_max_subqueries = 5

    @staticmethod
    def _get_structured_output(num_subqueries: int):
        return create_retriever_input_class(num_subqueries)

    def __init__(
        self,
        prompt_constructor: BasePrompt,
        llm: Optional[BaseChatModel] = None,
        max_subqueries: Optional[int] = None,
    ):
        """
        Initializes the base retrieval agent.

        Args:
            prompt_constructor: An instance of the prompt constructor.
            llm: The LangChain chat model to be used.
            max_subqueries: The maximum number of sub-queries to generate.
                    Defaults to predefined value.

        Raises:
            ValueError: If `max_subqueries` is not an integer greater than or equal to 1.
        """
        if max_subqueries is None:
            self._max_subqueries = self._default_max_subqueries
        
        else:
            if not isinstance(max_subqueries, int) or max_subqueries < 1:
                raise ValueError("'max_subqueries' must be an integer greater than or equal to 1.")
            
            self._max_subqueries = max_subqueries
        
        super().__init__(
            llm= llm or self._default_llm,
            prompt_constructor= prompt_constructor,
            structured_output= self._get_structured_output(self._max_subqueries),
        )


    @property
    def max_subqueries(self) -> Optional[int]:
        """Gets the maximum number of subqueries."""
        return self._max_subqueries

    @max_subqueries.setter
    def max_subqueries(self, value: int):
        """
        Sets the maximum number of subqueries and updates the structured output.

        Raises:
            ValueError: If the value is not an integer greater than or equal to 1.
        """
        if not isinstance(value, int) or value < 1:
            raise ValueError("'max_subqueries' must be an integer greater than or equal to 1.")
        
        if value != self._max_subqueries:
            self._max_subqueries = value
            self.structured_output = self._get_structured_output(value)


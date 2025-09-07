
from typing import Any, Callable, Dict, List, Literal, Optional, Type

from ..prompts import _RETRIEVAL_GRADER_DYNAMIC_PROMPT_DICT
from .base import BaseEdge, BaseAgenticConditionalEdge
from ..agents import (
    AnswerGrader,
    BaseAgent,
    HallucinationGrader,
    RetrievalGrader
)



class GradeRetrievedChunkEdge(BaseAgenticConditionalEdge):
    """
    A conditional edge that grades the relevance of a retrieved chunk.

    This edge decides the next step in the graph based on whether the provided
    chunk is relevant to the user's query.
    """

    _required_state_vars = ['user_query', 'chunk_txt']
    _output_property = 'relevant'
    _prompt_adjustments: Dict[str, Any] = _RETRIEVAL_GRADER_DYNAMIC_PROMPT_DICT


    def __init__(
        self,
        state_class: Type[Dict],
        is_relevant_next_step: str,
        no_relevance_next_step: str,
        required_state_vars: Optional[List[str]] = None,
        agent: Optional[BaseAgent] = None,
        output_property: Optional[str] = None,
        prompt_adjustments: Optional[Dict[str, Any]] = None,
    ):
        """
        Initializes the GradeRetrievedChunkEdge.

        Args:
            state_class: The TypedDict class representing the graph state.
            is_relevant_next_step: The node to call if the state variable is True.
            no_relevance_next_step: The node to call if the state variable is False.
            required_state_vars: An optional list of required state variables.
            agent: An optional pre-configured agent. If not provided, a default one is created.
            output_property: The name of the property expected in the agent's structured output.
            prompt_adjustments: A dictionary for adjusting the user query based on the entity.
        """
        super().__init__(
            state_class= state_class,
            required_state_vars= required_state_vars,
            agent= agent,
            output_property= output_property,
        )

        if not isinstance(is_relevant_next_step, str):
            raise TypeError("is_relevant_next_step must be a string.")
        self._is_relevant_next_step = is_relevant_next_step

        if not isinstance(no_relevance_next_step, str):
            raise TypeError("no_relevance_next_step must be a string.")
        self._no_relevance_next_step = no_relevance_next_step

        self._prompt_adjustments = prompt_adjustments or self._prompt_adjustments
        if not isinstance(self._prompt_adjustments, dict):
            raise TypeError("'prompt_adjustments' must be a dictionary.")


    @property
    def is_relevant_next_step(self) -> str:
        """Getter for the is_relevant_next_step property."""
        return self._is_relevant_next_step

    @is_relevant_next_step.setter
    def is_relevant_next_step(self, value: str):
        """Setter for the is_relevant_next_step property."""
        if not isinstance(value, str):
            raise TypeError("is_relevant_next_step must be a string.")
        self._is_relevant_next_step = value


    @property
    def no_relevance_next_step(self) -> str:
        """Getter for the no_relevance_next_step property."""
        return self._no_relevance_next_step

    @no_relevance_next_step.setter
    def no_relevance_next_step(self, value: str):
        """Setter for the no_relevance_next_step property."""
        if not isinstance(value, str):
            raise TypeError("no_relevance_next_step must be a string.")
        self._no_relevance_next_step = value


    @property
    def prompt_adjustments(self) -> Dict[str, Any]:
        """Getter for the 'prompt_adjustments' property."""
        return self._prompt_adjustments

    @prompt_adjustments.setter
    def prompt_adjustments(self, value: Dict[str, Any]):
        """Setter for the 'prompt_adjustments' property with validation."""
        if not isinstance(value, dict):
            raise TypeError("'prompt_adjustments' must be a dictionary.")
        self._prompt_adjustments = value


    def get_default_agent(self) -> RetrievalGrader:
        """
        Provides the default retrieval grader agent for this edge.

        Returns:
            An instance of the RetrievalGrader agent.
        """
        return RetrievalGrader()


    def get_edge_function(self) -> Callable[[Dict[str, Any]], str]:
        """
        Returns the callable function for this conditional edge.
        """
        
        agent_runnable = self.agent.get_runnable()
        
        def grade_retrieved_chunk(state: Dict[str, Any]) -> str:
            """
            Determines whether the retrieved document is relevant to the question.
            """
            print("--- GRADE CHUNK RELEVANCE TO QUESTION ❔ ---")
            
            user_query: str = state['user_query']
            entity = state.get('entity')
            chunk_txt = state['chunk_txt']
            
            full_user_query = user_query
            if entity and entity in self.prompt_adjustments:
                adjustment = self.prompt_adjustments[entity]['user_query']
                if not user_query.strip().upper().startswith(adjustment.strip().upper()):
                    full_user_query = f'{adjustment}"{user_query}"'
            
            relevant = getattr(
                agent_runnable.invoke(
                    {'user_query': full_user_query, 'chunk_txt': chunk_txt}
                ),
                self.output_property
            )

            if relevant:
                print("--- GRADE: RELEVANT CHUNK ✅ ---")
                return self.is_relevant_next_step
            else:
                print("--- GRADE: NOT RELEVANT CHUNK 🗑️ ---")
                return self.no_relevance_next_step
        
        return grade_retrieved_chunk



class GradeChunkSummaryGenerationEdge(BaseEdge):
    """
    A conditional edge node that determines the next step based on the quality 
    and relevance of the generated content.
    
    This node checks:
    1. The number of generation iterations to prevent infinite loops.
    2. Whether the generated content is grounded in the provided context (no hallucinations).
    3. Whether the generated content addresses the user's original query.
    """

    _required_state_vars = [
        'generate_iterations', 
        'user_query', 'chunk_txt', 'chunk_summary'
    ]
    _max_iterations: int = 3
    _prompt_adjustments: Dict[str, Any] = _RETRIEVAL_GRADER_DYNAMIC_PROMPT_DICT
    _hallucination_output_property = 'grounded'
    _answer_grader_output_property = 'addresses'


    def __init__(
        self,
        state_class: Type[Dict],
        retry_next_step: str,
        abort_next_step: str,
        end_next_step: str = '__end__',
        required_state_vars: Optional[List[str]] = None,
        max_iterations: Optional[int] = None,
        hallucination_grader: Optional[BaseAgent] = None,
        answer_grader: Optional[BaseAgent] = None,
        prompt_adjustments: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes the edge with its dependencies.
        
        Args:
            state_class: The TypedDict class for state validation.
            retry_next_step: The node to call if is needed to retry.
            abort_next_step: The node to call if failed and have to abort.
            end_next_step: The node to call if succed.
            required_state_vars: An optional list of required state variables.
            max_iterations: The maximum number of generation attempts.
            hallucination_grader: An agent to check for ungrounded content.
            answer_grader: An agent to check if the answer addresses the question.
            prompt_adjustments: A dictionary to adjust the prompt based on entity.
        """
        super().__init__(
            state_class= state_class, 
            required_state_vars= required_state_vars
        )

        if not isinstance(retry_next_step, str):
            raise TypeError("retry_next_step must be a string.")
        self._retry_next_step= retry_next_step

        if not isinstance(abort_next_step, str):
            raise TypeError("abort_next_step must be a string.")
        self._abort_next_step = abort_next_step

        if not isinstance(end_next_step, str):
            raise TypeError("end_next_step must be a string.")
        self._end_next_step = end_next_step

        self._max_iterations = max_iterations or self._max_iterations
        if self._max_iterations <= 1:
            raise ValueError("'max_iterations' must be an integer greater or equal to 1.")

        self._prompt_adjustments = prompt_adjustments or self._prompt_adjustments
        if self._prompt_adjustments is not None and not isinstance(self._prompt_adjustments, dict):
            raise TypeError("'prompt_adjustments' must be a dictionary.")

        self._hallucination_grader = hallucination_grader or self.get_default_hallucination_grader()
        self._validate_agent(
            self.hallucination_grader,
            self._hallucination_output_property,
            'hallucination_grader'
        )

        self._answer_grader = answer_grader or self.get_default_answer_grader()
        self._validate_agent(
            self.answer_grader,
            self._answer_grader_output_property,
            'answer_grader'
        )


    @property
    def retry_next_step(self) -> str:
        """Getter for the retry_next_step property."""
        return self._retry_next_step

    @retry_next_step.setter
    def retry_next_step(self, value: str):
        """Setter for the retry_next_step property."""
        if not isinstance(value, str):
            raise TypeError("retry_next_step must be a string.")
        self._retry_next_step = value


    @property
    def abort_next_step(self) -> str:
        """Getter for the abort_next_step property."""
        return self._abort_next_step

    @abort_next_step.setter
    def abort_next_step(self, value: str):
        """Setter for the abort_next_step property."""
        if not isinstance(value, str):
            raise TypeError("abort_next_step must be a string.")
        self._abort_next_step = value


    @property
    def end_next_step(self) -> str:
        """Getter for the end_next_step property."""
        return self._end_next_step

    @end_next_step.setter
    def end_next_step(self, value: str):
        """Setter for the end_next_step property."""
        if not isinstance(value, str):
            raise TypeError("end_next_step must be a string.")
        self._end_next_step = value


    @property
    def max_iterations(self) -> int:
        """Getter for the 'max_iterations' property."""
        return self._max_iterations

    @max_iterations.setter
    def max_iterations(self, value: int):
        """Setter for the 'max_iterations' property with validation."""
        if not isinstance(value, int) or value <= 1:
            raise ValueError("'max_iterations' must be an integer greather or equal 1.")
        self._max_iterations = value


    @property
    def hallucination_grader(self) -> BaseAgent:
        """Getter for the 'hallucination_grader' property."""
        return self._hallucination_grader

    @hallucination_grader.setter
    def hallucination_grader(self, value: BaseAgent):
        """Setter for the 'hallucination_grader' property with validation."""
        self._validate_agent(
            value,
            self._hallucination_output_property,
            'hallucination_grader'
        )
        self._hallucination_grader = value


    @property
    def hallucination_output_property(self) -> str:
        """Getter for the 'hallucination_output_property' property."""
        return self._hallucination_output_property

    @hallucination_output_property.setter
    def hallucination_output_property(self, value: str):
        """Setter for the 'hallucination_output_property' property."""
        self._hallucination_output_property = value


    @property
    def answer_grader(self) -> BaseAgent:
        """Getter for the 'answer_grader' property."""
        return self._answer_grader

    @answer_grader.setter
    def answer_grader(self, value: BaseAgent):
        """Setter for the 'answer_grader' property with validation."""
        self._validate_agent(
            value,
            self._answer_grader_output_property,
            'answer_grader'
        )
        self._answer_grader = value


    @property
    def answer_grader_output_property(self) -> str:
        """Getter for the 'answer_grader_output_property' property."""
        return self._answer_grader_output_property

    @answer_grader_output_property.setter
    def answer_grader_output_property(self, value: str):
        """Setter for the 'answer_grader_output_property' property."""
        self._answer_grader_output_property = value


    @property
    def prompt_adjustments(self) -> Dict[str, Any]:
        """Getter for the 'prompt_adjustments' property."""
        return self._prompt_adjustments

    @prompt_adjustments.setter
    def prompt_adjustments(self, value: Dict[str, Any]):
        """Setter for the 'prompt_adjustments' property with validation."""
        if not isinstance(value, dict):
            raise TypeError("'prompt_adjustments' must be a dictionary.")
        self._prompt_adjustments = value

    @staticmethod
    def get_default_hallucination_grader() -> HallucinationGrader:
        """
        Provides the default hallucination grader agent for this edge.
        
        Returns:
            An instance of the HallucinationGrader agent.
        """
        return HallucinationGrader()

    @staticmethod
    def get_default_answer_grader() -> AnswerGrader:
        """
        Provides the default answer grader agent for this edge.
        
        Returns:
            An instance of the AnswerGrader agent.
        """
        return AnswerGrader()


    def get_edge_function(self) -> Callable[[Dict[str, Any]], str]:
        """
        Returns the callable function for this graph node's edge.
        
        Returns:
            A function that takes the state dictionary and returns the next node's name.
        """
        
        hallucination_grader = self.hallucination_grader.get_runnable()
        answer_grader = self.answer_grader.get_runnable()


        def grade_chunk_summary_generation(state: Dict[str, Any]) -> str:
            """
            Determines the next step based on the generation's quality.
            """
            print("--- CHECK ITERATIONS 🔁 ---")
            generate_iterations = state.get('generate_iterations', 0)

            if generate_iterations >= self.max_iterations:
                print(f"--- DECISION: MAX ITERATIONS REACHED ({generate_iterations}) 🔚 ---")
                return self.abort_next_step


            print("--- GRADE HALLUCINATIONS 👻 ---")
            user_query: str = state['user_query']
            entity = state.get('entity')
            chunk_txt = state['chunk_txt']
            chunk_summary = state['chunk_summary'][0]

            grounded = getattr(
                hallucination_grader.invoke({
                    'chunk_txt': chunk_txt,
                    'chunk_summary': chunk_summary
                }),
                self.hallucination_output_property
            )

            if grounded:
                print("--- DECISION: GENERATION IS GROUNDED IN DOCUMENTS ✅ ---")

                full_user_query = user_query
                if entity and entity in self.prompt_adjustments:
                    full_user_query = (
                        user_query
                        if user_query.strip().upper().startswith(
                            self.prompt_adjustments[entity]['user_query'].strip().upper()
                        ) else
                        f'{self.prompt_adjustments[entity]["user_query"]}"{user_query}".'
                    )
                
                addresses = getattr(
                    answer_grader.invoke({
                        'user_query': full_user_query,
                        'chunk_summary': chunk_summary
                    }),
                    self.answer_grader_output_property
                )

                if addresses:
                    print("--- DECISION: GENERATION ADDRESSES QUESTION ✅ ---")
                    return self.end_next_step

                else:
                    print("--- DECISION: GENERATION DOES NOT ADDRESS QUESTION ❌ ---")
            else:
                print("--- DECISION: GENERATION IS NOT GROUNDED (HALLUCINATIONS) 👻❌ ---")

            return self.retry_next_step
        
        return grade_chunk_summary_generation


    def _validate_agent(
        self,
        agent: BaseAgent,
        output_field: str,
        agent_name: str
    ) -> None:
        """
        Validates that the agent has the required structured output fields.
        """
        if not agent.structured_output:
            raise ValueError(f"The agent '{agent_name}' must have a structured output.")
        
        if output_field not in agent.structured_output.model_json_schema()['properties']:
            raise AttributeError(
                f"The structured output of {agent_name} must have a '{output_field}' field."
            )



from typing import Any, Callable, Dict, List, Optional, Type

from .base import BaseNode
from ..prompts import _RETRIEVAL_GRADER_DYNAMIC_PROMPT_DICT
from ..agents import (
    BaseAgent,
    ChunkSummaryGenerator,
    BusinessLogicSummarizer,
    MdlSummarizer,
    GlobalContextGenerator,
    NoRelevantContextGenerator
)



class SummarizeChunkNode(BaseNode):
    """
    A generator node for chunk summarization based on retrieval chunk.

    This class specializes the `BaseNode` to summarize content from a context and
    validates the specific state attributes and agent output structure required.
    """

    _agent_validation_Type = 'structured_output'
    _required_state_vars = [
        'user_query', 'language', 
        'chunk_txt', 'chunk_summary', 
        'generate_iterations'
    ]
    _output_property = 'generated_content'
    _prompt_adjustments: Dict[str, Any] = _RETRIEVAL_GRADER_DYNAMIC_PROMPT_DICT


    def __init__(
        self,
        state_class: Type[Dict],
        required_state_vars: Optional[List[str]] = None,
        agent: Optional[BaseAgent] = None,
        output_property: Optional[str] = None,
        prompt_adjustments: Optional[Dict[str, Any]] = None
    ):
        """
        Initializes the node with optional overrides for class variables.
        """
        super().__init__(
            state_class= state_class,
            required_state_vars= required_state_vars,
            agent= agent,
            output_property= output_property
        )

        if prompt_adjustments is not None:
            if not isinstance(prompt_adjustments, dict):
                raise TypeError("prompt_adjustments must be a dictionary.")
            self._prompt_adjustments = prompt_adjustments


    @property
    def prompt_adjustments(self) -> Dict[str, Any]:
        """Getter for the prompt_adjustments property."""
        return self._prompt_adjustments
    
    @prompt_adjustments.setter
    def prompt_adjustments(self, value: Dict[str, Any]):
        """Setter for the prompt_adjustments property."""
        if not isinstance(value, dict):
            raise TypeError("prompt_adjustments must be a dictionary.")
        self._prompt_adjustments = value


    def get_default_agent(self) -> ChunkSummaryGenerator:
        """
        Provides a new default chunk summary generator agent for this node.
        
        Returns:
            A new instance of ChunkSummaryGenerator.
        """
        return ChunkSummaryGenerator()


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.
        
        Returns:
            A function that takes the state dictionary and returns an updated state.
        """

        agent_runnable = self.agent.get_runnable()

        def summarize_chunk(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Generate relevant content for a question based on a given context.
            
            This function processes the state, formats the input based on the entity,
            and uses the generator agent to create the final content. 
            
            Args:
                state: The current graph state.
                
            Returns:
                An updated state dictionary containing the generated content and
                an incremented iteration count.
            """
            print("--- SUMMARIZE CHUNK 📝📚 ---")
            user_query: str = state['user_query']
            language = state['language']
            entity = state.get('entity')
            chunk_txt = state['chunk_txt']
            generate_iterations = state.get('generate_iterations', 0)

            full_user_query = user_query
            output_requirements = ''

            if entity and entity in self.prompt_adjustments:
                full_user_query = (
                    user_query
                    if user_query.strip().upper().startswith(
                        self.prompt_adjustments[entity]['user_query'].strip().upper()
                    ) else
                    f'{self.prompt_adjustments[entity]["user_query"]}"{user_query}".'
                )
                output_requirements = self.prompt_adjustments[entity]['output']

            chunk_summary = getattr(
                agent_runnable.invoke({
                    "language": language,
                    "user_query": full_user_query,
                    "chunk_txt": chunk_txt,
                    "output_requirements": output_requirements,
                }),
                self.output_property
            )

            return {
                'chunk_summary': [chunk_summary],
                'generate_iterations': generate_iterations + 1
            }
        
        return summarize_chunk



class SummarizeBusinessLogicNode(BaseNode):
    """
    A generator node for consolidating and summarizing business logic context.

    This class specializes the `BaseNode` to generate a summary based on a list of
    content chunks and validates the specific state attributes and agent output.
    """

    _agent_validation_Type = 'structured_output'
    _required_state_vars = [
        'user_query', 'language', 
        'chunk_summary', 'business_logic'
    ]
    _output_property = 'generated_summary'


    def get_default_agent(self) -> BusinessLogicSummarizer:
        """
        Provides a new default business logic summarizer agent for this node.
        
        Returns:
            A new instance of BusinessLogicSummarizer.
        """
        return BusinessLogicSummarizer()


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.

        Returns:
            A function that takes the state dictionary and returns an updated state.
        """

        agent_runnable = self.agent.get_runnable()

        def summarize_business_logic(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Consolidates and summarizes business logic context.

            Args:
                state: The current graph state.

            Returns:
                An updated state dictionary containing the summarized business logic.
            """
            print("--- SUMMARIZE BUSINES LOGIC 📝👨‍💼 ---")
            
            user_query = state['user_query']
            language = state["language"]
            generation = [
                generation_result
                for generation_result in state['chunk_summary']
                if generation_result != '[NO RELEVANT CONTENT]'
            ]

            if not generation:
                return {
                    'business_logic': 'Business logic for this request was not found. Please try a different query.'
                }

            context = '\n\n---\n\n'.join(generation)

            business_logic_summary = getattr(
                agent_runnable.invoke({
                    "user_query": user_query,
                    "language": language,
                    "context": context
                }),
                self.output_property
            )

            return {
                'business_logic': business_logic_summary
            }
        
        return summarize_business_logic



class SummarizeMdlNode(BaseNode):
    """
    A generator node for consolidating and summarizing MDL data context.

    This class specializes the `BaseNode` by implementing the logic for generating
    a summary of relevant data schemas and validating the required state attributes
    and agent output.
    """

    _agent_validation_Type = 'structured_output'
    _required_state_vars = [
        'user_query', 'language', 
        'chunk_summary', 'data_schema'
    ]
    _output_property = 'generated_summary'


    def get_default_agent(self) -> MdlSummarizer:
        """
        Provides a new default mdl data schema summarizer agent for this node.

        Returns:
            An instance of the MdlSummarizer agent.
        """
        return MdlSummarizer()


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.

        Returns:
            A function that takes the state dictionary and returns an updated state.
        """

        agent_runnable = self.agent.get_runnable()

        def summarize_mdl(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Consolidates and summarizes MDL data context.

            Args:
                state: The current graph state.

            Returns:
                An updated state dictionary containing the summarized data schema.
            """
            print("--- SUMMARIZE MDL 📝🗂️ ---")
            
            user_query = state['user_query']
            language = state['language']
            generation = [
                generation_result
                for generation_result in state['chunk_summary']
                if generation_result != '[NO RELEVANT CONTENT]'
            ]

            if not generation:
                return {
                    'data_schema': 'Relevant tables and columns for this request were not found. Please try a different query.'
                }

            context = '\n\n---\n\n'.join(generation)

            data_schema = getattr(
                agent_runnable.invoke({
                    "user_query": user_query,
                    "language": language,
                    "context": context
                }),
                self.output_property
            )

            return {
                'data_schema': data_schema
            }

        return summarize_mdl



class GenerateGlobalContextNode(BaseNode):
    """
    A generator node for creating a global context from business logic
    and data schema summaries.

    This class specializes the `BaseNode` to synthesize a comprehensive
    context based on distinct knowledge sources, which is useful for tasks
    like SQL generation.
    """

    _agent_validation_Type = 'structured_output'
    _required_state_vars = [
        'user_query', 'language', 
        'business_logic', 'data_schema', 
        'context'
    ]
    _output_property = 'generated_context'


    def get_default_agent(self) -> GlobalContextGenerator:
        """
        Provides a new default global context generator agent for this node.

        Returns:
            An instance of the GlobalContextGenerator agent.
        """
        return GlobalContextGenerator()


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.

        Returns:
            A function that takes the state dictionary and returns an updated state.
        """

        agent_runnable = self.agent.get_runnable()

        def generate_global_context(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Generates a global context based on provided business logic and data schema.

            Args:
                state: The current graph state.

            Returns:
                An updated state dictionary containing the generated global context.
            """
            print("--- GENERATE GLOBAL CONTEXT 📝🌐 ---")
            
            user_query = state['user_query']
            language = state['language']
            business_logic = state['business_logic']
            data_schema = state['data_schema']

            context = getattr(
                agent_runnable.invoke({
                    "user_query": user_query,
                    "language": language,
                    "business_logic": business_logic,
                    "data_schema": data_schema
                }),
                self.output_property
            )

            return {
                'context': context
            }
        
        return generate_global_context



class GenerateNoContextResponseNode(BaseNode):
    """
    A generator node for creating an explanatory response when no relevant context is found.

    This class specializes the `BaseNode` to inform the user about the lack of
    relevant information and provides helpful examples to guide them.
    """

    _agent_validation_Type = 'structured_output'
    _required_state_vars = [
        'user_query', 'language',
        'business_logic_retrieval_results',
        'mdl_retrieval_results',
        'no_relevant_context_msg'
    ]
    _output_property = 'no_context_message'


    def get_default_agent(self) -> NoRelevantContextGenerator:
        """
        Provides a new default no relevant context response generator agent for this node.

        Returns:
            An instance of the NoRelevantContextGenerator agent.
        """
        return NoRelevantContextGenerator()


    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
        """
        Returns the callable function for this graph node.

        Returns:
            A function that takes the state dictionary and returns an updated state.
        """

        agent_runnable = self.agent.get_runnable()
        
        def generate_no_context_response(state: Dict[str, Any]) -> Dict[str, Any]:
            """
            Generates an explanation for the user with examples when no relevant context is found.

            Args:
                state: The current graph state.

            Returns:
                An updated state dictionary containing the no-context message.
            """
            print("--- GENERATE NO RELEVANT CONTEXT RESPONSE 📝⛔ ---")
            
            user_query = state['user_query']
            language = state['language']
            business_logic_retrieval_results = state['business_logic_retrieval_results']
            mdl_retrieval_results = state['mdl_retrieval_results']

            context_list = ['### Business Logic Context']
            context_list.extend([business_logic_txt for business_logic_txt in business_logic_retrieval_results])
            context_list.append('### Tables Context')
            context_list.extend([
                '\n'.join(table['table_summary'].split('\n')[2:])
                for table in mdl_retrieval_results
            ])

            context_retrieved_summary = '\n\n---\n\n'.join(context_list)

            no_relevant_context_msg = getattr(
                agent_runnable.invoke({
                    "user_query": user_query,
                    "language": language,
                    "context": context_retrieved_summary,
                }),
                self.output_property
            )

            return {
                'no_relevant_context_msg': no_relevant_context_msg
            }
        
        return generate_no_context_response


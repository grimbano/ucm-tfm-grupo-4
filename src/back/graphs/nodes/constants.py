
from typing import Any, Callable, Dict, List

class SetRetrievalGradeOutputKoNode:
    """
    A class that generates a callable node function to set the output to a
    predefined 'no relevant content' message.

    This node is used in a graph to provide a fallback response when other
    processes fail to find or generate relevant content.
    """

    def get_node_function(self) -> Callable[[Dict[str, Any]], Dict[str, List[str]]]:
        """
        Returns the callable function for this graph node.

        The returned function takes the current state and returns a dictionary
        indicating that no relevant content was found.
        
        Returns:
            A function that sets the 'generation' key in the state to a list
            containing the '[NO RELEVANT CONTENT]' message.
        """

        def set_retrieval_grade_output_ko(state: Dict[str, Any]) -> Dict[str, List[str]]:
            """
            Sets the generation output to a 'no relevant content' message.

            Args:
                state: The current graph state.
                
            Returns:
                A dictionary with the generation message.
            """
            print("--- SET RETRIEVAL GRADE OUTPUT KO ❌ ---")
            return {
                'generation': ['[NO RELEVANT CONTENT]']
            }
        
        return set_retrieval_grade_output_ko


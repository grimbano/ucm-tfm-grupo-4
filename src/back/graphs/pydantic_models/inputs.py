
from typing import List
from pydantic import BaseModel, Field


def create_retriever_input_class(max_subqueries: int):
    """
    Creates a Pydantic class with a dynamic `max_subqueries` value.
    """
    
    description = (
        "A list of one or more search queries to retrieve relevant information.\n"
        f"Break down the user's question into up to {max_subqueries} simple, "
        "focused sub-queries to maximize retrieval accuracy.\n"
        "Each sub-query should represent a key concept from the original question."
    )
    
    class RetrieverInput(BaseModel):
        """
        Input schema for retriever tools. Accepts one or more queries for retrieval.
        """
        queries: List[str] = Field(description= description)

    return RetrieverInput


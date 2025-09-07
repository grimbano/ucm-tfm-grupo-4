
import operator
from typing import Annotated, Dict, List, TypedDict


class ChunkProcessingState(TypedDict):
    user_query: str
    language: str
    entity: str
    chunk_txt: str
    generate_iterations: int
    chunk_summary: List[str]


class BusinessLogicState(TypedDict):
    user_query: str
    language: str
    entity: str
    sub_queries: List[str]
    retieval_iterations: int
    retrieval_results: List[str]
    business_logic_retrieval_results: List[str]
    chunk_summary: Annotated[List[str], operator.add]
    business_logic: str


class MdlState(TypedDict):
    user_query: str
    language: str
    entity: str
    sub_queries: List[str]
    retieval_iterations: int
    retrieval_results: List[str]
    mdl_retrieval_results: List[Dict[str, str]]
    chunk_summary: Annotated[List[str], operator.add]
    data_schema: str


class ContextGeneratorState(TypedDict):
    user_query: str
    language: str
    context_generation_iterations: int
    business_logic: str
    data_schema: str
    relevant_context: bool
    context: str
    no_relevant_context_msg: str
    mdl_retrieval_results: List[Dict[str, str]]
    business_logic_retrieval_results: List[str]



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
    business_logic: str
    data_schema: str
    db_name: str
    schema_name: str
    relevant_context: bool
    context: str
    no_relevant_context_msg: str
    mdl_retrieval_results: List[Dict[str, str]]
    business_logic_retrieval_results: List[str]


class QueryGeneratorState(TypedDict):
    context: str
    user_query: str
    query_examples: str
    sql_candidate: str
    error_msg: str
    attempt: Annotated[int, operator.add]
    max_attempts: int
    notes: Annotated[List[str], operator.add]
    dialect: str
    language: str
    sql_query: str
    valid_query_generated: bool


class MainGraphState(TypedDict):
    user_query: str
    language: str
    relevant_context: bool
    context: str
    db_name: str
    schema_name: str
    no_relevant_context_msg: str
    sql_query: str
    valid_query_generated: bool
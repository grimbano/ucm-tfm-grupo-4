
import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict

from .auxs import DbStateVar


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


class QueryValidatorState(TypedDict):
    user_query: str
    context: str
    db_name: str
    schema_name: str
    sql_query: str
    db: Optional[DbStateVar]
    table_names: List[str]
    tables_info: List[str]
    query_results: List[Dict[str, Any]]
    query_validation_error_msg: Optional[str]
    retries: int
    valid_query_execution: bool


class ConclusionsGeneratorState(TypedDict):
    user_query: str
    sql_query: str
    language: str
    query_results: str
    graphs_retries: int
    nl_output: str
    sql_explanation: str
    graphics_json: str


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
    table_names: List[str]
    tables_info: List[str]
    query_results: List[Dict[str, Any]]
    valid_query_execution: bool
    query_validation_error_msg: Optional[str]
    nl_output: str
    sql_explanation: str
    graphics_json: Optional[str]
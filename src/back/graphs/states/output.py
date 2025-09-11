
from typing import Any, Dict, List, Optional, TypedDict


class ChunkProcessingOutputState(TypedDict):
    chunk_summary: List[str]


class BusinessLogicOutputState(TypedDict):
    business_logic_retrieval_results: List[str]
    business_logic: str


class MdlOutputState(TypedDict):
    mdl_retrieval_results: List[Dict[str, str]]
    data_schema: str


class ContextGeneratorOutputState(TypedDict):
    language: str
    db_name: str
    schema_name: str
    relevant_context: bool
    context: str
    no_relevant_context_msg: str


class QueryGeneratorOutputState(TypedDict):
    sql_query: str
    valid_query_generated: bool


class QueryValidatorOutputState(TypedDict):
    sql_query: str
    table_names: List[str]
    tables_info: List[str]
    query_results: List[Dict[str, Any]]
    valid_query_execution: bool
    query_validation_error_msg: Optional[str]


class ConclusionsGeneratorOutputState(TypedDict):
    nl_output: str
    sql_explanation: str
    graphics_json: str


class MainGraphOutputState(TypedDict):
    global_execution_ok: bool
    nl_output: str
    sql_explanation: str
    graphics_json: Optional[str]
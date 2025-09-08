

from typing import Dict, List, TypedDict


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
    relevant_context: bool
    context: str
    no_relevant_context_msg: str



from typing import List
from pydantic import BaseModel, Field


########## CLASSIFIERS ##########

class LanguageClassifierResult(BaseModel):
    """Detect the language of the user query."""
    language: str = Field(
        description= "Language of user query in English, e.g. Spanish, English, etc."
    )


########## GRADERS ##########

class BusinessRelevanceGraderResult(BaseModel):
    """
    Boolean score to determine if a query is relevant to 
    business and can be answered with a data warehouse.
    """
    relevant_question: bool = Field(
        description="The query is business-relevant and answerable by data, `true` or `false`."
    )

class RetrievalGraderResult(BaseModel):
    """Boolean score for relevance check on retrieved documents."""
    relevant: bool = Field(
        description= "The document is relevant to the question, `true` or `false`"
    )

class HallucinationGraderResult(BaseModel):
    """Boolean score for hallucination present in generation answer."""
    grounded: bool = Field(
        description= "Answer is grounded in the facts, `true` or `false`"
    )

class AnswerGraderResult(BaseModel):
    """Boolean score to assess answer addresses question."""
    addresses: bool = Field(
        description= "Answer addresses the question, `true` or `false`"
    )

class GlobalRetrievalGraderResult(BaseModel):
    """Boolean score for relevance check on business context to user query."""
    relevant_context: bool = Field(
        description="The business context is relevant to the user query, `true` or `false`"
    )

class QueryCoherenceGraderResult(BaseModel):
    """
    Determina si una query SQL es coherente con la intención del mensaje de usuario,
    basándose en un resumen de alto nivel de las tablas.
    """
    coherent: bool = Field(
        description="""
        Un valor booleano que indica si la query SQL es 'coherente' (True)
        con el mensaje del usuario, dada la información contextual.
        Devuelve True si la query es correcta y resuelve la pregunta del usuario.
        Devuelve False si la query es incorrecta, incompleta o no se alinea con el
        mensaje del usuario o el contexto.
        """
    )


########## EXTRACTORS ##########

class DbSchemaExtractionResult(BaseModel):
    """
    Structured output for extracting database and schema names.
    """
    db_name: str = Field(
        description= "The name of the database where the data is stored. If not found, set to '[Not found]'."
    )
    schema_name: str = Field(
        description= "The name of the schema within the database. If not found, set to '[Not found]'."
    )

class TablesExtractionResult(BaseModel):
    """
    Structured output for extracting table names from an SQL query.
    """
    table_names: List[str] = Field(
        description= "The name of the tables presents in a SQL query. If not found, retrieve an empty list."
    )


########## GENERATORS ##########

class OnFailResponseGeneratorResult(BaseModel):
    """The final message to be shown to the user when a process has failed."""
    nl_output: str = Field(
        description="A polite and clear message explaining why the request could not be fulfilled."
    )

class ChunkSummaryGeneratorResult(BaseModel):
    """Relevant content generated from bringed context based in user query."""
    generated_content: str = Field(
        description= "Brief content generated using bringed context."
    )

class BusinessLogicSummarizerResult(BaseModel):
    """Relevant summary generated from document retrival based in user query."""
    generated_summary: str = Field(
        description= "Summary of the relevant content in business logic chunks retrieval."
    )

class MdlSummarizerResult(BaseModel):
    """Relevant summary generated from document retrival based in user query."""
    generated_summary: str = Field(
        description= "Summary of the relevant content in tables summaries and columns details retrieval."
    )

class GlobalContextGeneratorResult(BaseModel):
    """Relevant global summary generated from business logic and tables schemas based in user query."""
    generated_context: str = Field(
        description= "Global summary of business logic and tables schemas relevant for a data analyst SQL query confection."
    )

class NoRelevantContextGeneratorResult(BaseModel):
    """
    Generate a concise apology to the user when the AI's knowledge base lacks relevant information
    to answer the query. The message should include some example topics the AI can discuss.
    """
    no_context_message: str = Field(
        description= (
            "A polite and apologetic message to the user, explaining that the current "
            "knowledge base does not contain information on the topic. The message must "
            "also offer to answer questions on other topics based in the context bringed."
        )
    )


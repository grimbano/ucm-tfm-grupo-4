
from pydantic import BaseModel, Field


########## CLASSIFIERS ##########

class LanguageClassifierResult(BaseModel):
    """Detect the language of the user query."""
    language: str = Field(
        description= "Language of user query in English, e.g. Spanish, English, etc."
    )


########## GRADERS ##########

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


########## GENERATORS ##########

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


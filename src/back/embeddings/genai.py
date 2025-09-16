

from typing import List, Optional
from langchain.embeddings.base import Embeddings
from google import genai

from src.utils.customs import GenaiEmbedConfigTaskType


class GenAIExtendedEmbeddingFunction(Embeddings):
    """
    A custom embedding function that extends LangChain's Embeddings class
    to support the Gemini API via Vertex AI.

    This class is implemented as a workaround because the native LangChain
    integration for Google's GenAI models does not currently support using
    Vertex AI for embedding generation, a crucial feature for many production
    deployments on Google Cloud Platform.
    """

    def __init__(self, model: str):
        """
        Initializes the class with the Gemini model.
        
        Args:
            model: The name of the Gemini model to use for embeddings
                    (e.g., 'gemini-embedding-001').
        """
        self.model = model
        self.genai_client = genai.Client()


    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generates embeddings for a list of documents.

        This method is required by the LangChain Embeddings interface. It calls
        the internal embedding method with the 'retrieval_document' task type,
        which is optimized for document-based retrieval.

        Args:
            texts: A list of strings representing documents.

        Returns:
            A list of lists of floats, where each inner list is an embedding vector.
        """
        return self._get_genai_embeddings(
            contents= texts,
            task_type= GenaiEmbedConfigTaskType.RETRIEVAL_DOCUMENT
        )


    def embed_query(self, text: str) -> List[float]:
        """
        Generates an embedding for a single query string.

        This method is required by the LangChain Embeddings interface. It calls
        the internal embedding method with the 'retrieval_query' task type,
        which is optimized for query-based retrieval.

        Args:
            text: The query string to embed.

        Returns:
            A list of floats representing the embedding vector.
        """
        return self._get_genai_embeddings(
            contents= [text],
            task_type= GenaiEmbedConfigTaskType.RETRIEVAL_QUERY
        )[0]


    def _get_genai_embeddings(self, contents: List[str], task_type: Optional[GenaiEmbedConfigTaskType] = None) -> List[List[float]]:
        """
        Internal method to get embeddings from the GenAI API via Vertex AI.

        This method handles the API call and response parsing for embedding generation.

        Args:
            contents: A list of strings to embed.
            task_type: The task type for the embedding (e.g., 'retrieval_document').
        
        Returns:
            A list of lists of floats, where each inner list is an embedding vector.
        """
        embed_config = genai.types.EmbedContentConfig(task_type=task_type.value) if task_type else None
        
        response = self.genai_client.models.embed_content(
            model= self.model,
            contents= contents,
            config= embed_config
        )
        
        return [embed.values for embed in response.embeddings]


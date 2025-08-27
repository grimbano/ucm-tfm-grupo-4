"""This is the custom embeddings package.

It contains embeddings with the configuration requirements for our project.
"""

from .genai import GenAIExtendedEmbeddingFunction

__all__ = [
    'GenAIExtendedEmbeddingFunction',
]
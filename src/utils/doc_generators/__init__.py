"""This is the doc_generators package.

It contains classes and functions for generating differents texts and docs.
"""

from .mdl_generator import BaseMdlGenerator
from .sql_generator import get_create_table_as

__all__ = [
    'BaseMdlGenerator',
    'get_create_table_as',
]
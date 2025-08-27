"""This is the utils splitters package.

It contains many different splitters for chunks generation.
"""

from .json_splitter import JsonExamplesSplitter
from .md_splitter import ExtendedMarkdownSplitter
from .mdl_splitter import MdlSplitter

__all__ = [
    'JsonExamplesSplitter'
    'ExtendedMarkdownSplitter',
    'MdlSplitter',
]
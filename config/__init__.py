"""This is the configuration package.

It contains functions to get relevant configurations for the source packages.
"""

from .settings import get_pg_config

__all__ = [
    'get_pg_config'
]
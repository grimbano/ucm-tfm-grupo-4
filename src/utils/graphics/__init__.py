"""This is the graphics package.

It contains functions to create graphical content.
"""

from .plotly_graphs import create_dashboard_from_json


__all__ = [
    'create_dashboard_from_json',
]
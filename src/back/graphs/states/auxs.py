
from typing import TypedDict

from langchain_community.utilities import SQLDatabase
from sqlalchemy import Engine


class DbStateVar(TypedDict):
    table_info: SQLDatabase
    engine: Engine
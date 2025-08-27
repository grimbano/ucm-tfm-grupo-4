

from pathlib import Path
from typing import Literal, Tuple, TypeAlias, Union

from langchain_core.documents import Document


FilePath: TypeAlias = Union[str, Path]
DocumentWithScore: TypeAlias = Tuple[Document, float]
InformationSchemaFormat: TypeAlias = Literal['list_dict', 'pandas']
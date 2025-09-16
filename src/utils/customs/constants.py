

from enum import Enum
from typing import Literal, Tuple


class BaseQueryField(str, Enum):
    """
    Enum for mapping information schema query results to standardized field names.

    This centralizes the field names used in the base SQL query, making them
    easier to manage and less prone to typos.
    """
    DB_NAME = 'db_name'
    SCHEMA_NAME = 'schema_name'
    TABLE_NAME = 'table_name'
    COLUMN_NAME = 'column_name'
    COLUMN_TYPE = 'column_type'
    PRIMARY_KEY = 'primary_key'
    FOREIGN_KEY = 'foreign_key'
    TARGET = 'target'


class ChunkKey(Enum):
    """An enumeration for standard metadata keys used in document chunking."""
    FILE_NAME = 'file_name'
    HEADERS_CHUNK_ID = 'headers_chunk_id'
    HEADERS_CHUNKS_TOTAL = 'headers_comb_total'
    CHUNK_OVERLAP = 'chunk_overlap'
    MIN = 'min'
    MAX = 'max'
    TOTAL = 'total'
    MIN_ID = 'min_id'
    MAX_ID = 'max_id'
    TOTAL_CHUNKS = 'total_chunks'

    EXTRA_CHUNKS_METADATA: Tuple = (
        FILE_NAME,
        HEADERS_CHUNK_ID,
        HEADERS_CHUNKS_TOTAL,
        CHUNK_OVERLAP
    )


class GenaiEmbedConfigTaskType(str, Enum):
    """
    Enum representing the different task types for GenAI embeddings.
    
    The value of each member is the same as its name.
    """
    CLASSIFICATION = 'CLASSIFICATION'
    CLUSTERING = 'CLUSTERING'
    RETRIEVAL_DOCUMENT = 'RETRIEVAL_DOCUMENT'
    RETRIEVAL_QUERY = 'RETRIEVAL_QUERY'
    QUESTION_ANSWERING = 'QUESTION_ANSWERING'
    FACT_VERIFICATION = 'FACT_VERIFICATION'
    CODE_RETRIEVAL_QUERY = 'CODE_RETRIEVAL_QUERY'
    SEMANTIC_SIMILARITY = 'SEMANTIC_SIMILARITY'


class HierarchicalKey(str, Enum):
    """
    Defines the standard keys used in the hierarchical search results.

    This Enum provides a consistent set of string keys for accessing
    data related to tables and columns in a structured hierarchical
    format, ensuring type safety and code readability.
    """
    TABLE_SUMMARY = 'table_summary'
    COLUMNS = 'columns'
    ID = 'id'
    CONTENT = 'content'
    RELEVANCE_SCORE = 'relevance_score'


class MdlKey(str, Enum):
    """
    Enum for keys used in the Model-Driven Language (MDL) data structure.
    
    This class centralizes all string constants to prevent errors and improve
    code readability.
    """
    DATABASE = 'database'
    SCHEMAS = 'schemas'
    TABLES = 'tables'
    COLUMNS = 'columns'
    NAME = 'name'
    DESCRIPTION = 'description'
    PRIMARY_KEY = 'is_primary_key'
    FOREIGN_KEY = 'is_foreign_key'
    DATA_TYPE = 'data_type'
    REFERENCE = 'reference'
    TABLE_ID = 'table_id'
    DATABASE_NAME = 'database_name'
    SCHEMA_NAME = 'schema_name'
    TABLE_NAME = 'table_name'
    COLUMN_NAME = 'column_name'
    COLUMN_DATA_TYPE = 'column_data_type'


class SqlCommand(Enum):
    """Represents a collection of standard SQL commands.

    This enumeration groups common SQL commands into Data Definition Language (DDL) 
    and Data Manipulation Language (DML) for clear categorization.
    """
    CREATE = 'CREATE'
    DROP = 'DROP'
    ALTER = 'ALTER'

    INSERT = 'INSERT'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'

    CTE = 'WITH'
    SELECT = 'SELECT'

    DDL_COMMANDS: Tuple = (CREATE, DROP, ALTER)
    DML_COMMANDS: Tuple = (INSERT, UPDATE, DELETE)
    QUERY_BEGINNERS: Tuple = (CTE, SELECT)


import os
from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union
import uuid

from langchain_core.documents import Document
import yaml

from ..customs import ChunkKey, FilePath, MdlKey


class MdlSplitter:
    """A class to handle the entire chunking process for MDL data.

    This class is responsible for loading MDL (Metadata Language) data from a
    YAML file, processing the data, and creating two distinct sets of Document
    objects: one for table summaries and another for individual columns. This
    approach allows for a dual-level representation of the data model, which is
    useful for different downstream tasks, such as RAG (Retrieval-Augmented
    Generation) queries targeting either high-level table information or
    specific column details.
    """

    def __init__(self):
        """Initializes the MdlSplitter instance.

        The constructor currently has no parameters and serves to initialize
        the class, readying it for subsequent calls to its splitting methods.
        """
        pass
    

    def split_text(
        self,
        mdl_data: Dict,
        file_name: str
    ) -> Tuple[List[Document], List[Document]]:
        """Splits MDL data into two types of documents: table chunks and column chunks.

        This function processes a dictionary of MDL data, extracting information
        about databases, schemas, tables, and columns. It generates a list of
        documents for table summaries (including primary and foreign keys) and
        a list of documents for individual columns.

        Args:
            mdl_data: A dictionary containing the MDL data, typically loaded from a YAML file.
            file_name: The name of the file from which the data was loaded.

        Returns:
            A tuple containing two lists of Document objects:
            - The first list contains documents representing table summaries.
            - The second list contains documents representing individual columns.

        Raises:
            ValueError: If `file_name` is not provided.
        """
        if not file_name:
            raise ValueError("The 'file_name' argument must be provided and cannot be empty.")

        table_chunks = []
        column_chunks = []

        database_name = mdl_data[MdlKey.DATABASE.value]

        for schema in mdl_data[MdlKey.SCHEMAS.value]:
            schema_name = schema[MdlKey.NAME.value]

            for table in schema[MdlKey.TABLES.value]:
                table_name = table[MdlKey.NAME.value]
                table_description = table[MdlKey.DESCRIPTION.value]
                table_columns = table[MdlKey.COLUMNS.value]

                table_chunk_content_list = [
                    f'Database: {database_name}',
                    f'Schema: {schema_name}',
                    f'Table: {table_name}',
                    f'Table description: {table_description}'
                ]


                table_primary_key = [
                    f'- {col[MdlKey.NAME.value]}'
                    for col in table_columns 
                    if col.get(MdlKey.PRIMARY_KEY.value)
                ]
                if table_primary_key:
                    table_chunk_content_list.append('Table PRIMARY KEY:')
                    table_chunk_content_list.extend([pk for pk in table_primary_key])


                table_foreign_keys = [
                    f'- ({col[MdlKey.NAME.value]}, {col[MdlKey.REFERENCE.value]})'
                    for col in table_columns 
                    if col.get(MdlKey.FOREIGN_KEY.value)
                ]
                if table_foreign_keys:
                    table_chunk_content_list.append('Table FOREIGN KEYS (Column name, Reference):')
                    table_chunk_content_list.extend([fk for fk in table_foreign_keys])
                

                table_id = str(uuid.uuid4())
                table_metadata = {
                    ChunkKey.FILE_NAME.value: file_name,
                    MdlKey.TABLE_ID.value: table_id,
                    MdlKey.DATABASE_NAME.value: database_name,
                    MdlKey.SCHEMA_NAME.value: schema_name,
                    MdlKey.TABLE_NAME.value: table_name
                }


                table_chunks.append(Document(
                    id= table_id,
                    page_content= '\n'.join(table_chunk_content_list),
                    metadata = table_metadata
                ))


                for col in table_columns:
                    if col.get(MdlKey.PRIMARY_KEY.value) or col.get(MdlKey.FOREIGN_KEY.value):
                        continue

                    column_chunk_content_list = []

                    column_name = col[MdlKey.NAME.value]
                    column_data_type = col[MdlKey.DATA_TYPE.value]
                    column_description = col[MdlKey.DESCRIPTION.value]

                    column_chunk_content_list.append(f'Column name: {column_name}')
                    column_chunk_content_list.append(f'Column data type: {column_data_type}')
                    column_chunk_content_list.append(f'Column description: {column_description}')
                    
                    column_metadata = deepcopy(table_metadata)
                    column_metadata[MdlKey.COLUMN_NAME.value] = column_name
                    column_metadata[MdlKey.COLUMN_DATA_TYPE.value] = column_data_type

                    column_chunks.append(Document(
                        id= str(uuid.uuid4()),
                        page_content= '\n'.join(column_chunk_content_list),
                        metadata = column_metadata
                    ))


        return (table_chunks, column_chunks)


    def split_documents(
        self,
        mdl_file_paths: Union[FilePath, List[FilePath]],
        encoding: Optional[str] = None
    ) -> Tuple[List[Document], List[Document]]:
        """Loads and splits one or more MDL files, returning a single tuple of flattened document lists.

        This method processes a single file path or a list of file paths to MDL YAML files. 
        It aggregates all table documents into one list and all column documents into another, 
        returning them as a single tuple of two flattened lists.

        Args:
            mdl_file_paths: A single path or a list of paths to the MDL YAML files.
            encoding: The optional encoding to use for the files.

        Returns:
            A tuple containing two lists:
            - The first list is a single, flattened list of all table documents from all processed files.
            - The second list is a single, flattened list of all column documents from all processed files.
        """
        is_single_file = not isinstance(mdl_file_paths, list)
        _mdl_file_paths = [mdl_file_paths] if is_single_file else mdl_file_paths

        all_table_chunks = []
        all_column_chunks = []

        for mdl_file_path in _mdl_file_paths:
            table_chunks, column_chunks = self.split_text(
                mdl_data= self._load_mdl_data(mdl_file_path, encoding),
                file_name= os.path.basename(mdl_file_path)
            )

            all_table_chunks.extend(table_chunks)
            all_column_chunks.extend(column_chunks)

        return (all_table_chunks, all_column_chunks)


    def _load_mdl_data(
        self,
        mdl_file_path: FilePath,
        encoding: Optional[str] = None
    ) -> Dict:
        """Loads and parses data from a YAML file.

        This is an internal method that reads a file at a given path,
        parses its content as YAML, and returns it as a dictionary.

        Args:
            mdl_file_path: The path to the YAML file.
            encoding: The optional encoding to use for the file.

        Returns:
            A dictionary containing the parsed YAML data.

        Raises:
            ValueError: If the file path does not have a '.yaml' or '.yml' extension.
            FileNotFoundError: If the file at the specified path does not exist.
            YAMLError: If an error occurs during the YAML parsing process.
        """
        file_path_str = str(mdl_file_path)

        if not file_path_str.lower().endswith(('.yaml', '.yml')):
            raise ValueError(
                f"Invalid file extension: '{file_path_str}'. The 'mdl_file_path' "
                f"must refer to a valid YAML file with a '.yaml' or '.yml' extension."
            )

        try:
            with open(mdl_file_path, 'r', encoding= encoding) as mdl_file:
                return yaml.safe_load(mdl_file)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at '{mdl_file_path}' was not found.")
        
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")




import os
from typing import Dict, List, Optional, Union, Any
import uuid

from langchain_core.documents import Document
import json

from ..customs import ChunkKey, FilePath


class JsonExamplesSplitter:
    """
    A splitter for JSON files containing a list of dictionaries (examples).

    This splitter processes JSON files where each element in the root-level list
    is an "example" dictionary. It extracts a designated field as the document's
    page content and other specified fields as metadata, creating a `Document`
    object for each example.
    """

    def __init__(
        self, 
        page_content_key: str,
        metadata_keys: Optional[List[str]] = None
    ):
        """
        Initializes the JsonExamplesSplitter.

        Args:
            page_content_key: The key in the JSON examples whose value will
                    be used as the Document's page content.
            metadata_keys: A list of keys whose values will be included in the
                    Document's metadata. If None, all keys except the 
                    'page_content_key' are used.
        """
        if not page_content_key:
            raise ValueError("The 'page_content_key' cannot be empty or None.")
        
        self._page_content_key = page_content_key
        self._metadata_keys = metadata_keys
        pass


    @property
    def page_content_key(self) -> str:
        """The key used for the document's page content."""
        return self._page_content_key
    
    @page_content_key.setter
    def page_content_key(self, new_key: str):
        if not new_key:
            raise ValueError("The 'page_content_key' cannot be empty or None.")
        self._page_content_key = new_key


    @property
    def metadata_keys(self) -> str:
        """The keys used for the document's metadata."""
        return self._page_content_key
    
    @metadata_keys.setter
    def metadata_keys(self, new_keys: Optional[List[str]] = None):
        self._metadata_keys = new_keys


    def split_text(
        self,
        json_data: List[Dict[str, Any]],
        file_name: str
    ) -> List[Document]:
        """
        Splits a list of JSON examples into LangChain Document objects.

        Args:
            json_data: A list of dictionaries, where each dictionary 
                    represents a data example.
            file_name: The name of the original file, used for metadata.

        Returns:
            A list of Document objects created from the data.
        """
        documents = []

        for i, example in enumerate(json_data):
            try:
                page_content = example[self._page_content_key]
            except KeyError:
                raise KeyError(
                    f"The specified page content key '{self._page_content_key}' "
                    f"was not found in example at index {i}."
                )
            
            metadata = {ChunkKey.FILE_NAME.value: file_name}

            if self._metadata_keys:
                for metadata_key in self._metadata_keys:
                    metadata[metadata_key] = example.get(metadata_key)

            documents.append(Document(
                id= str(uuid.uuid4()),
                page_content= page_content,
                metadata= metadata.copy()
            ))
        
        return documents


    def split_documents(
        self,
        json_file_paths: Union[FilePath, List[FilePath]],
        encoding: Optional[str] = None,
    ) -> List[Document]:
        """
        Loads and splits documents from one or more JSON files.

        Args:
            json_file_paths: A single file path or a list of file paths.
            encoding: The encoding to use when reading the files.

        Returns:
            A list of Document objects from all processed files.
        """
        is_single_file = not isinstance(json_file_paths, list)
        _json_file_paths = [json_file_paths] if is_single_file else json_file_paths

        all_documents = []

        for json_file_path in _json_file_paths:
            try:
                example_chunks = self.split_text(
                    json_data= self._load_json_data(json_file_path, encoding),
                    file_name= os.path.basename(json_file_path)
                )

                all_documents.extend(example_chunks)

            except Exception as e:
                raise RuntimeError(
                    f"An error occurred while processing file '{json_file_path}': {e}"
                ) from e

        return all_documents


    def _load_json_data(
        self,
        json_file_path: FilePath,
        encoding: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Loads JSON data from a file and performs validation.

        Args:
            json_file_path: The path to the JSON file.
            encoding: The encoding to use when reading the file.

        Returns:
            The loaded JSON data.

        Raises:
            ValueError: If the file extension is invalid or the data format is incorrect.
            FileNotFoundError: If the specified file does not exist.
        """
        file_path_str = str(json_file_path)

        if not file_path_str.lower().endswith(('.json', '.jsonl')):
            raise ValueError(
                f"Invalid file extension: '{file_path_str}'. The 'json_file_path' "
                f"must refer to a valid JSON file with a '.json' or '.jsonl' extension."
            )


        try:
            with open(json_file_path, 'r', encoding= encoding) as json_file:
                json_data = json.load(json_file)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"The file at '{json_file_path}' was not found.")
        
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON from file '{file_path_str}': {e}")
        
        except Exception as e:
            raise IOError(f"An unexpected error occurred while reading file '{file_path_str}': {e}")


        if not isinstance(json_data, list):
            raise ValueError(
                "The JSON data must be a list of examples (dictionaries). "
                f"Instead, it is a '{type(json_data).__name__}'."
            )
        
        if not json_data:
            return []
        
        first_example = json_data[0]
        if self._page_content_key not in first_example:
            raise ValueError(
                f"The specified page content key '{self._page_content_key}' "
                "was not found in the first example of the loaded data."
            )
        
        if self._metadata_keys is None:
            self._set_metadata_keys_based_on_json_data(json_data)

        return json_data


    def _set_metadata_keys_based_on_json_data(
        self,
        json_data: List[Dict[str, Any]]
    ):
        """
        Automatically sets metadata keys based on the first example in the JSON data.
        
        Args:
            json_data: The loaded JSON data.
        """
        if not json_data:
            self._metadata_keys = []
            return
        
        first_example_keys = json_data[0].keys()
        self._metadata_keys = [
            key
            for key in first_example_keys
            if key != self._page_content_key
        ]


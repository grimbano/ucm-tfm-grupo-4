

import os
from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Union
import uuid

from langchain_core.documents import Document
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
import regex

from ..customs import ChunkKey, FilePath


class ExtendedMarkdownSplitter:
    """An extended Markdown splitter for creating structured document chunks.
    
    This class combines a MarkdownHeaderTextSplitter and a RecursiveCharacterTextSplitter
    to provide a more robust and customizable way to split Markdown files. It handles
    splitting by headers, further splitting by character limits, and enriches
    document metadata with header information, chunk IDs, and file names.
    """
    BASE_MD_HEADERS_NAMES = {
        1: 'title',
        2: 'subtitle',
        3: 'section',
        4: 'sub-section',
        5: 'detail'
    }

    def __init__(
        self,
        chunk_size: int,
        chunk_overlap: int,
        headers_to_split_on: Optional[List[Tuple[str, str]]] = None,
    ):
        """Initializes the ExtendedMarkdownSplitter.

        Args:
            chunk_size: The target size of each document chunk.
            chunk_overlap: The number of characters to overlap between chunks.
            headers_to_split_on: A list of header tuples to define the splitting
                    strategy. If None, this will be determined automatically when
                    `split_documents` is called with `update_headers_to_split_on=True`.
        """
        self._auto_md_headers_names = self.BASE_MD_HEADERS_NAMES.copy()

        self._chunk_size = chunk_size
        self._chunk_overlap = chunk_overlap
        self._update_recursive_splitter_definition()

        self._headers_to_split_on = headers_to_split_on
        if headers_to_split_on is not None:
            self._update_markdown_splitter_definition()


    @property
    def auto_md_headers_names(self) -> Dict[int, str]:
        """The dictionary mapping header levels to their names."""
        return self._auto_md_headers_names
    
    @auto_md_headers_names.setter
    def auto_md_headers_names(self, new_headers_names: Dict[int, str]):
        """Sets a new mapping of header levels to custom names.
        
        Args:
            new_headers_names: A dictionary with integer keys for header levels
                    and string values for their names.
        """
        self._auto_md_headers_names = new_headers_names


    @property
    def chunk_size(self) -> int:
        """The size of each text chunk after splitting the document."""
        return self._chunk_size
    
    @chunk_size.setter
    def chunk_size(self, new_size: int):
        """Sets the size of each text chunk.
        
        Args:
            new_size: The new chunk size. Must be a positive integer.
        """
        self._chunk_size = new_size
        self._update_recursive_splitter_definition()


    @property
    def chunk_overlap(self) -> int:
        """The number of characters to overlap between adjacent chunks."""
        return self._chunk_overlap

    @chunk_overlap.setter
    def chunk_overlap(self, new_overlap: int):
        """Sets the number of characters to overlap between chunks.
        
        Args:
            new_overlap: The new chunk overlap. Must be a non-negative integer.
        """
        self._chunk_overlap = new_overlap
        self._update_recursive_splitter_definition()


    @property
    def headers_to_split_on(self) -> List[Tuple[str, str]]:
        """A list of headers to split the document by."""
        return self._headers_to_split_on

    @headers_to_split_on.setter
    def headers_to_split_on(self, new_headers:  List[Tuple[str, str]]):
        """Sets the list of headers to split the document by.
        
        Args:
            new_headers: The new list of header tuples.
        """
        self._headers_to_split_on = new_headers
        self._update_markdown_splitter_definition()


    def split_text(self, md_text: str, file_name: str) -> List[Document]:
        """Splits a single Markdown text string into a list of Document objects.

        This method processes the input Markdown text by first splitting it based on
        headers, then recursively splitting the resulting chunks. It adds and refines
        metadata, including a unique ID for each document, file name, chunk tags,
        and header information, ensuring a complete and structured output.

        Args:
            md_text: The Markdown text to be split.
            file_name: The name of the file from which the text was loaded.

        Returns:
            A list of Document objects, each representing a structured chunk of the original text.

        Raises:
            ValueError: If `headers_to_split_on` is not defined before the method is called.
        """
        if not self._headers_to_split_on:
            raise ValueError(
                "The headers to split on must be defined before calling `split_text`. "
                "You can do this by passing `headers_to_split_on` during initialization "
                "or by using `split_documents` with `update_headers_to_split_on=True`."
            )
        
        documents = self._markdown_splitter.split_text(self._add_trailing_dot_to_md(md_text))
        documents = [doc for doc in documents if doc.metadata]
        documents = self._remove_trailing_dot_to_md(documents)
        documents = self._clean_md_text_formatting(documents)
        documents = self._recursive_splitter.split_documents(documents)
        documents = self._set_documents_id(documents)
        documents = self._set_file_name_in_metadata(documents, file_name)
        documents = self._fill_missing_headers_in_metadata(documents)
        documents = self._tag_chunks_by_headers(documents)
        documents = self._set_chunk_overlap_in_metadata(documents)

        return documents


    def split_documents(
        self,
        md_file_paths: Union[FilePath, List[FilePath]],
        encoding: Optional[str] = None,
        autodetect_encoding: bool = False,
        update_headers_to_split_on: bool = True
    ) -> List[Document]:
        """Splits one or more Markdown files into a list of Document objects.

        This method loads the content from the specified Markdown file paths,
        splits the content, and adds relevant metadata to each chunk. It can
        also automatically detect headers from the first file to split on.

        Args:
            md_file_paths: A single path or a list of paths to Markdown files.
            encoding: The encoding of the files.
            autodetect_encoding: Whether to automatically detect the file encoding.
            update_headers_to_split_on: If True, headers will be automatically
                    set based on the first file processed.

        Returns:
            A list of all Document objects from the processed files.
        """
        is_single_file = not isinstance(md_file_paths, list)
        _md_file_paths = [md_file_paths] if is_single_file else md_file_paths

        all_documents = []

        for md_file_path in _md_file_paths:
            md_text = self._load_md_text(
                md_file_path,
                encoding,
                autodetect_encoding,
                update_headers_to_split_on
            )

            all_documents.extend(self.split_text(md_text, os.path.basename(md_file_path)))

        return all_documents


    def _update_markdown_splitter_definition(self):
        """Updates the MarkdownHeaderTextSplitter instance with current settings."""
        self._markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on= self._headers_to_split_on,
            return_each_line= False,
            strip_headers= False,
        )


    def _update_recursive_splitter_definition(self):
        """Updates the RecursiveCharacterTextSplitter instance with current settings."""
        self._recursive_splitter = RecursiveCharacterTextSplitter(
            separators= [
                r'\n\d+\.\d+\s+',     # sub-subsections ex. 2.1, 3.4
                r'\n\d+\.\s+',        # subsections ex. 1., 2., 3.
                r'\n\s*```',          # fences of code blocks (```sql ... ```)
                r';\s*\n',            # ends of SQL queries (opcional pero muy útil)
                r'\n{2,}',            # double line break (paragraphs)
                r'\n',                # simple line break
                r' ',                 # spaces
                r''                   # fallback to character level
            ],
            is_separator_regex= True,
            chunk_size= self._chunk_size,
            chunk_overlap= self._chunk_overlap
        )


    def _load_md_text(
        self, 
        md_file_path: FilePath,
        encoding: Optional[str] = None,
        autodetect_encoding: bool = False,
        update_headers_to_split_on: bool = True
    ) -> str:
        """Loads and reads the text from a Markdown file.

        Args:
            md_file_path: The path to the Markdown file.
            encoding: The encoding of the file.
            autodetect_encoding: Whether to autodetect the encoding.
            update_headers_to_split_on: If True, updates headers based on
                    the file content.

        Returns:
            The content of the Markdown file as a string.

        Raises:
            ValueError: If the file path does not end with '.md'.
        """
        file_path_str = str(md_file_path).lower()

        if not file_path_str.endswith('.md'):
            raise ValueError(
                f"Invalid file path: '{file_path_str}'. The 'md_file_path' "
                f"must refer to a valid Markdown file (e.g., 'document.md')."
            )

        md_text = TextLoader(
            file_path= md_file_path,
            encoding= encoding,
            autodetect_encoding= autodetect_encoding
        ).load()[0].page_content

        if update_headers_to_split_on:
            self._set_auto_md_headers_tuples(md_text)

        return md_text


    def _set_auto_md_headers_tuples(
        self,
        md_text: str,
        init_level: int = 2
    ) -> List[Tuple[str]]:
        """Sets headers to split on based on the content of the Markdown text.

        This method scans the text for headers from `init_level` to level 6 and
        creates the `headers_to_split_on` list.

        Args:
            md_text: The Markdown text to be scanned for headers.
            init_level: The starting header level to check for.
        """
        self._headers_to_split_on = [
            (
                '#' * processing_level,
                f"{processing_level}_{self._auto_md_headers_names.get(processing_level, 'minimum')}"
            )
            for processing_level in range(init_level, 7)
            if md_text.find('#' * processing_level) != -1
        ]

        self._update_markdown_splitter_definition()



    def _add_trailing_dot_to_md(self, md_text: str) -> str:
        """Adds a trailing dot to lines that are not headers to preserve them.

        This method is a workaround to ensure that MarkdownHeaderTextSplitter
        doesn't discard content that isn't under a header.

        Args:
            md_text: The Markdown text to process.

        Returns:
            The text with dots added to non-header lines.
        """
        return '\n'.join([
            '.' + line if not regex.match(r'^#+\s.+$', line) else line
            for line in md_text.split('\n')
        ])


    def _remove_trailing_dot_to_md(self, documents: List[Document]) -> List[Document]:
        """Removes a leading dot from each line of a list of Document objects.

        This function processes each document in the provided list and removes the 
        first character of each line if it is a dot ('.'). This is the inverse 
        operation of `_add_trailing_dot_to_md` and is used to restore the original
        text content after splitting.

        Args:
            documents: A list of Document objects, each with content that may have 
                    leading dots.

        Returns:
            A new list of Document objects with the leading dots removed from their
            `page_content`.
        """
        updated_documents = []

        for doc in documents:
            updated_content = '\n'.join([
                line[1:] if regex.match(r'^\..*$', line) else line
                for line in doc.page_content.split('\n')
            ])

            updated_documents.append(Document(page_content= updated_content, metadata= doc.metadata))

        return updated_documents


    def _clean_md_text_formatting(self, documents: List[Document]) -> List[Document]:
        """Removes common Markdown formatting from a list of documents.

        This function iterates through each document and processes its content to remove
        various Markdown syntax, including headers, bold, italics, strikethrough, and 
        underlined text. It is designed to preserve the basic structure of lists and 
        their prefixes (e.g., '-', '*', '+').

        The process involves:
        1. Iterating over each line of a document's `page_content`.
        2. Skipping horizontal rule lines (`---` or `***`).
        3. Identifying and preserving list prefixes.
        4. Removing Markdown headers and other inline formatting using regular expressions.
        5. Appending the cleaned lines to create a new `Document` object.

        Args:
            documents: A list of LangChain Document objects with Markdown formatting.

        Returns:
            A new list of Document objects with the Markdown formatting removed from 
            their `page_content`.
        """
        updated_documents = []

        for doc in documents:
            cleaned_lines = []

            lines_pattern = regex.compile(r'^\s*(---|\*\*\*|\+\+\+)\s*$')
            list_prefix_pattern = regex.compile(r'^(\s*[-*+])\s')

            heading_pattern = regex.compile(r'^\s*#+\s(.+)$')
            bold_italic_pattern = regex.compile(r'(?<=^|\s|\p{P})\*\*\*(.*?)\*\*\*(?=\s|\p{P}|$)')
            bold_pattern = regex.compile(r'(?<=^|\s|\p{P})\*\*(.*?)\*\*(?=\s|\p{P}|$)')
            italic_pattern = regex.compile(r'(?<=^|\s|\p{P})\*(.*?)\*(?=\s|\p{P}|$)')
            bold_italic_underline_pattern = regex.compile(r'(?<=^|\s|\p{P})___(.*?)___(?=\s|\p{P}|$)')
            bold_underline_pattern = regex.compile(r'(?<=^|\s|\p{P})__(.*?)__(?=\s|\p{P}|$)')
            italic_underline_pattern = regex.compile(r'(?<=^|\s|\p{P})_(.*?)_(?=\s|\p{P}|$)')
            strike_through_pattern = regex.compile(r'(?<=^|\s|\p{P})~(.*?)~(?=\s|\p{P}|$)')
            underline_pattern = regex.compile(r'(?<=^|\s|\p{P})<u>(.*?)</u>(?=\s|\p{P}|$)')

            for line in doc.page_content.split('\n'):
                if lines_pattern.match(line):
                    continue

                list_prefix_match = list_prefix_pattern.match(line)
                prefix = list_prefix_match.group(1) if list_prefix_match else ''
                content = line[len(prefix):]

                content = heading_pattern.sub(r'\1', content)
                content = bold_italic_pattern.sub(r'\1', content)
                content = bold_pattern.sub(r'\1', content)
                content = italic_pattern.sub(r'\1', content)
                content = bold_italic_underline_pattern.sub(r'\1', content)
                content = bold_underline_pattern.sub(r'\1', content)
                content = italic_underline_pattern.sub(r'\1', content)
                content = strike_through_pattern.sub(r'\1', content)
                content = underline_pattern.sub(r'\1', content)

                cleaned_lines.append(prefix + content)

            updated_documents.append(Document(page_content= '\n'.join(cleaned_lines), metadata= doc.metadata))

        return updated_documents


    def _set_file_name_in_metadata(
        self,
        documents: List[Document],
        file_name: str
    ) -> List[Document]:
        """Adds the file name to the metadata of each document.

        Args:
            documents: A list of Document objects.
            file_name: The name of the file to be added to metadata.

        Returns:
            A new list of documents with the file name added to their metadata.

        Raises:
            ValueError: If `file_name` is not provided.
        """
        if not file_name:
            raise ValueError(
                "The 'file_name' argument must be provided and cannot be empty."
            )

        final_documents = deepcopy(documents)

        for doc in final_documents:
            doc.metadata[ChunkKey.FILE_NAME.value] = file_name

        return final_documents


    def _fill_missing_headers_in_metadata(
        self,
        documents: List[Document],
        headers_tuples: Optional[List[Tuple[str]]] = None
    ) -> List[Document]:
        """Ensures all specified header keys are present in document metadata.

        This method iterates through a list of documents and checks if each
        document's metadata contains all header keys defined in `headers_tuples`.
        If a key is missing, it's added to the metadata with a default value of 'N/A'.
        This standardizes the metadata schema across all documents.

        Args:
            documents: A list of LangChain Document objects to process.
            headers_tuples: A list of header tuples to use for standardizing keys.
                    If None, the instance's `_headers_to_split_on` property is used.

        Returns:
            A new list of Document objects with standardized metadata.
        """
        _headers_tuples = self._headers_to_split_on if headers_tuples is None else headers_tuples

        if _headers_tuples is None:
            raise ValueError(
                "Headers to split on are not defined. They must be set either "
                "during initialization or by processing a document first."
            )

        final_documents = deepcopy(documents)

        for doc in final_documents:
            for _, header_key in _headers_tuples:
                if header_key not in doc.metadata:
                    doc.metadata[header_key] = 'N/A'

        return final_documents


    def _tag_chunks_by_headers(
        self,
        documents: List[Document],
        headers_tuples: Optional[List[Tuple[str]]] = None
    ) -> List[Document]:
        """Assigns sequential chunk IDs and total counts based on header combinations.

        This function processes a list of documents in two passes. First, it
        counts the number of documents for each unique combination of header values.
        Second, it assigns a sequential ID to each chunk within its header
        combination and adds both the ID and the total count to the document's
        metadata. This provides a clear way to track document chunks within their
        hierarchical context.

        Args:
            documents: A list of LangChain Document objects.
            headers_tuples: A list of tuples containing the header-level
                    and metadata key to use for chunk tagging. If None, the
                    instance's `_headers_to_split_on` is used.

        Returns:
            A new list of Document objects with the chunk ID and total count
            added to their metadata.
        """
        _headers_tuples = self._headers_to_split_on if headers_tuples is None else headers_tuples

        if _headers_tuples is None:
            raise ValueError(
                "Headers to split on are not defined. They must be set either "
                "during initialization or by processing a document first."
            )

        final_documents = deepcopy(documents)
        combination_counts = {}

        for doc in final_documents:
            current_headers_tuple = tuple(doc.metadata.get(header_key) for _, header_key in _headers_tuples)
            combination_counts[current_headers_tuple] = combination_counts.get(current_headers_tuple, 0) + 1

        headers_comb_chunk_ids = {}
        for doc in final_documents:
            current_headers_tuple = tuple(doc.metadata.get(header_key) for _, header_key in _headers_tuples)
            chunk_id = headers_comb_chunk_ids.get(current_headers_tuple, 0)

            doc.metadata[ChunkKey.HEADERS_CHUNK_ID.value] = chunk_id
            doc.metadata[ChunkKey.HEADERS_CHUNKS_TOTAL.value] = combination_counts[current_headers_tuple]

            headers_comb_chunk_ids[current_headers_tuple] = chunk_id + 1

        return final_documents


    def _set_chunk_overlap_in_metadata(
        self,
        documents: List[Document],
        chunk_overlap: Optional[int] = None
    ) -> List[Document]:
        """Adds chunk overlap metadata to each document.

        This method adds a specified chunk overlap value to the metadata of each 
        document in a list. It uses a deep copy to avoid modifying the original
        documents in place.

        Args:
            documents: A list of LangChain Document objects.
            chunk_overlap: The integer value for the chunk overlap.
                    If None, the instance's `_chunk_overlap` property is used.

        Returns:
            A new list of Document objects with the chunk overlap metadata added.
        """
        
        _chunk_overlap = self._chunk_overlap if chunk_overlap is None else chunk_overlap
        final_documents = deepcopy(documents)

        for doc in final_documents:
            doc.metadata[ChunkKey.CHUNK_OVERLAP.value] = _chunk_overlap

        return final_documents


    def _set_documents_id(
        self,
        documents: List[Document]
    ) -> List[Document]:
        """Assigns a unique ID to each document in a list.

        This method creates a deep copy of the input list of documents to prevent
        modifying the original objects. It then iterates through the copied list,
        assigning a new, universally unique identifier (UUID) as a string to the `id`
        attribute of each document.

        Args:
            documents: A list of Document objects.

        Returns:
            A new list of Document objects, each with a unique string UUID assigned
            to its `id` attribute.
        """
        final_documents = deepcopy(documents)

        for doc in final_documents:
            doc.id = str(uuid.uuid4())

        return final_documents


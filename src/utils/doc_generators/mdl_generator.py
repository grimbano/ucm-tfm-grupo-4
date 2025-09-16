

from collections import OrderedDict, defaultdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pandas as pd
import yaml

from src.back.pg_sql import BasePostgres
from ..customs import BaseQueryField, InformationSchemaFormat, MdlKey

yaml.add_representer(OrderedDict, lambda dumper, data: dumper.represent_dict(data.items()))


class BaseMdlGenerator:
    """
    Generates base MDL (Model Definition Language) files from a database's
    information schema.

    This class orchestrates the process of querying a database, parsing the
    results, and formatting them into a human-editable YAML structure.
    """

    def __init__(
        self,
        base_query_path: str,
        env_file_path: Optional[str] = None
    ):
        """
        Initializes the generator with the path to the base SQL query file.

        Args:
            base_query_path: The file path to the SQL query.
            env_file_path: The path to a specific .env file. Defaults to None.

        Raises:
            FileNotFoundError: If the file path does not exist.
            ValueError: If the file does not have a '.sql' extension.
        """

        if not Path(base_query_path).exists():
            raise FileNotFoundError(
                f"The specified path does not exist: '{base_query_path}'. "
                "Please ensure the path to your SQL query file is correct."
            )
        
        if not base_query_path.lower().endswith('.sql'):
            raise ValueError(
                f"Invalid file extension: '{base_query_path}'. "
                "The 'base_query_path' must refer to a valid SQL file with a '.sql' extension."
            )
        
        self.base_query_path = base_query_path
        self.base_query = self._load_base_query(base_query_path)
        self._db_manager = BasePostgres()


    def get_information_schema_data(
        self,
        target_db_names: Union[str, List[str]],
        target_schema_names: Union[str, List[str]],
        format: InformationSchemaFormat = 'list_dict'
    ) -> Union[pd.DataFrame, List[dict], None]:
        """
        Retrieves information schema data from the database.

        Args:
            target_db_names: A list of database names or a single string.
            target_schema_names: A list of schema names or a single string.
            format: The desired output format (LIST_DICT or PANDAS).

        Returns:
            The information schema data in the requested format (DataFrame or list of dicts),
            or None if no data is found.
        """
        
        db_names = (
            [target_db_names] 
            if isinstance(target_db_names, str) 
            else list(target_db_names)
        )

        schema_names = (
            [target_schema_names] 
            if isinstance(target_schema_names, str) 
            else list(target_schema_names)
        )

        information_schema_data = self._execute_target_query(db_names, schema_names)

        if not information_schema_data:
            return None

        if format == 'pandas':
            information_schema_data = pd.DataFrame(information_schema_data)

        return information_schema_data


    def create_base_mdl_files(
        self,
        output_path: str,
        target_db_names: Union[str, List[str]],
        target_schema_names: Union[str, List[str]],
        encoding: Optional[str] = None,
        to_do_text: str = '[To be completed ...]'
    ) -> List[str]:
        """Generates base MDL YAML files for specified databases and schemas.

        This method retrieves metadata (information schema) from the database and
        structures it into base MDL YAML files. These files contain database, schema,
        and table definitions with a placeholder text for descriptions, which can be
        manually completed later.

        Args:
            output_path: The directory where the MDL YAML files will be saved.
            target_db_names: The name or a list of names of the target databases to process.
            target_schema_names: The name or a list of names of the target schemas to process.
            encoding: The optional encoding to use for the files. 
            to_do_text: The placeholder string to use for all `description` fields.

        Returns:
            A list of paths (strings) to the newly created MDL files.

        Raises:
            ValueError: If no information schema data is found for the specified databases and schemas.
            FileNotFoundError: If the specified `output_path` directory does not exist.
        """
        
        information_schema_data = self.get_information_schema_data(target_db_names, target_schema_names)
        
        if not information_schema_data:
            raise ValueError(
                "No information schema data was found for the specified database and schema names. "
                "Please check the `target_db_names` and `target_schema_names` parameters and ensure "
                "they match existing databases and schemas."
            )
        
        if not Path(output_path).exists():
            raise FileNotFoundError(
                f"The specified output path does not exist: '{output_path}'. "
                "Please create the directory before running the function."
            )
        
        output_mdl_file_paths = []
        
        dbs_data = self._group_data_by_hierarchy(information_schema_data)

        for db_name, schemas_data in dbs_data.items():
            db = OrderedDict()
            db[MdlKey.DATABASE.value] = db_name
            db[MdlKey.DESCRIPTION.value] = to_do_text

            schemas = list()
            for schema_name, tables_data in schemas_data.items():
                schema = OrderedDict()
                schema[MdlKey.NAME.value] = schema_name
                schema[MdlKey.DESCRIPTION.value] = to_do_text

                tables = list()
                for table_name, columns_data in tables_data.items():
                    table = OrderedDict()
                    table[MdlKey.NAME.value] = table_name
                    table[MdlKey.DESCRIPTION.value] = to_do_text

                    columns = list()
                    for column_data in columns_data:
                        column = OrderedDict()
                        column[MdlKey.NAME.value] = column_data.get(BaseQueryField.COLUMN_NAME.value)
                        column[MdlKey.DESCRIPTION.value] = to_do_text
                        column[MdlKey.DATA_TYPE.value] = column_data.get(BaseQueryField.COLUMN_TYPE.value)
                        
                        if column_data.get(BaseQueryField.PRIMARY_KEY.value):
                            column[MdlKey.PRIMARY_KEY.value] = True

                        if column_data.get(BaseQueryField.FOREIGN_KEY.value):
                            column[MdlKey.FOREIGN_KEY.value] = True
                            column[MdlKey.REFERENCE.value] = column_data.get(BaseQueryField.TARGET.value)

                        columns.append(column)

                    table[MdlKey.COLUMNS.value] = columns
                    tables.append(table)
                
                schema[MdlKey.TABLES.value] = tables
                schemas.append(schema)
            
            db[MdlKey.SCHEMAS.value] = schemas

            mdl_file_path = f'{output_path}/MDL_{db_name}.yaml'
            with open(mdl_file_path, 'w', encoding= encoding) as mdl:
                mdl.write(self._format_yaml(yaml.dump(db)))
            
            output_mdl_file_paths.append(mdl_file_path)

        return output_mdl_file_paths


    def _load_base_query(self, base_query_path: str) -> str:
        """
        Loads the content of the SQL query file.

        Args:
            base_query_path: The file path to the SQL query.

        Returns:
            The content of the SQL file as a string.
        """

        return Path(base_query_path).read_text()


    def _execute_target_query(
        self,
        target_db_names: Tuple[str],
        target_schema_names: Tuple[str]
    ) -> Union[List[dict], None]:
        """
        Executes the base SQL query against the target databases and schemas.

        Args:
            target_db_names: A list of database names to query.
            target_schema_names: A list of schema names to query.

        Returns:
            A list of dictionaries representing the query results, or None if the query fails.
        """

        db_placeholders = ', '.join(['%s'] * len(target_db_names))
        schema_placeholders = ', '.join(['%s'] * len(target_schema_names))

        final_query = self.base_query.replace('IN (%s)', f'IN ({db_placeholders})', 1)
        final_query = final_query.replace('IN (%s)', f'IN ({schema_placeholders})', 1)

        query_parameters = tuple(target_db_names + target_schema_names)

        return self._db_manager.execute_query(final_query, query_parameters)


    def _group_data_by_hierarchy(self, data: List[Dict]) -> defaultdict:
        """
        Groups information schema data by database, schema, and table.

        Args:
            data: A list of dictionaries representing the information schema query results.

        Returns:
            A defaultdict object with a nested structure (db -> schema -> table -> [columns]).
        """

        grouped_data = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

        for row in data:
            db_name = row.get(BaseQueryField.DB_NAME.value)
            schema_name = row.get(BaseQueryField.SCHEMA_NAME.value)
            table_name = row.get(BaseQueryField.TABLE_NAME.value)
            
            grouped_data[db_name][schema_name][table_name].append(row)

        return grouped_data


    def _format_yaml(self, yaml_str: str) -> str:
        """
        Formats a YAML string for better human readability.
        
        Note: This is a manual reformatting, which might not be robust for
        all YAML structures. It's often better to configure the YAML dumper
        to handle this automatically if possible.

        Args:
            yaml_str: The YAML string to format.
        
        Returns:
            The formatted YAML string.
        """
        
        last_line = ''
        last_line_list_init = False
        last_line_empty = False

        lines = list()

        for line in yaml_str.split('\n'):
            if line.strip().startswith('-') and not last_line_list_init and not last_line_empty:
                last_line += '\n'

            lines.append(last_line)
            last_line = line
            last_line_list_init = last_line.strip().endswith(':')
            last_line_empty = last_line.strip()==''

        lines.append(line)

        return '\n'.join(lines)



from typing import Optional, List, Dict, Any

import psycopg2
from psycopg2.extras import RealDictCursor

from config import get_pg_config
from src.utils.customs import SqlCommand


class BasePostgres:
    """Manages database connections and SQL command execution for a PostgreSQL database.

    This class provides a single, encapsulated interface for all database interactions,
    handling connection pooling and command execution. The database configuration is
    stored internally and is not directly accessible from outside the class.
    """

    def __init__(self, env_file_path: Optional[str] = None):
        """Initializes the database manager with a given configuration.

        Args:
            env_file_path: The path to a specific .env file. Defaults to None.
        """
        self.__db_config = get_pg_config(env_file_path).model_dump()


    def get_connection(self, port: Optional[int] = None) -> psycopg2.connect:
        """Establishes and returns a database connection.
        
        This private method handles the connection logic, allowing for a temporary
        port override if needed.
        """
        pg_config = self.__db_config.copy()

        connection_params = {
            'host': pg_config.get('POSTGRES_HOST'),
            'port': pg_config.get('DB_PORT'),
            'dbname': pg_config.get('POSTGRES_DB'),
            'user': pg_config.get('POSTGRES_USER'),
            'password': pg_config.get('POSTGRES_PASSWORD'),
        }

        if port:
            pg_config['db_port'] = port
        
        try:
            return psycopg2.connect(**connection_params)
        
        except psycopg2.DatabaseError as e:
            print(f"Database connection error: {e}")
            raise


    def execute_commands(self, commands: list[str], port: Optional[int] = None) -> None:
        """Executes a list of SQL DDL/DML commands against the database.

        This function takes a list of SQL commands and executes them sequentially.
        It ensures that only valid DDL (Data Definition Language) and DML
        (Data Manipulation Language) commands are executed.

        Args:
            commands: A list of SQL commands to execute. Each command must be
                    a valid DDL or DML command.
            port: An integer to force a different port than the .env one.
                    Defaults to None.

        Raises:
            ValueError: If any command in the list is not a valid DDL or DML command.
            psycopg2.DatabaseError: If there is a database error during execution.
        """
        valid_commands = {cmd for cmd in SqlCommand.DDL_COMMANDS.value} | {cmd for cmd in SqlCommand.DML_COMMANDS.value}
        
        for command in commands:
            first_word = command.strip().upper().split()[0]
            if first_word not in valid_commands:
                raise ValueError(f"Invalid command found: '{first_word}'. Only DDL/DML commands are allowed.")

        try:
            with self.get_connection(port) as connection:
                with connection.cursor() as cursor:
                    for command in commands:
                        cursor.execute(command)
                        print(f'\nThe following command was executed successfully:\n{command}')
                connection.commit()

        except psycopg2.DatabaseError as e:
            raise e
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise


    def execute_query(self, query: str, params: Optional[list] = None, port: Optional[int] = None) -> List[Dict[str, Any]]:
        """Executes a SQL SELECT query and returns the results as a list of dictionaries.

        This function is designed to be secure against SQL injection by using
        parameterized queries.

        Args:
            query: The SQL SELECT query to execute, with placeholders.
            params: A list of values to substitute for the placeholders.
                    Defaults to None.
            port: An integer to force a different port than the .env one.
                    Defaults to None.

        Returns:
            A list of dictionaries representing the query results, or an empty
            list if no rows are found.
        """
        first_word = query.strip().upper().split()[0]
        if first_word not in SqlCommand.QUERY_BEGINNERS.value:
            raise ValueError(f"The query must be {SqlCommand.QUERY_BEGINNERS.value} command.")

        query_results: List[Dict[str, Any]] = []

        try:
            with self.get_connection(port) as connection:
                with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                    if params:
                        cursor.execute(query, params)
                    else:
                        cursor.execute(query)
                    
                    query_results = cursor.fetchall()

        except psycopg2.DatabaseError as e:
            raise e
        
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            raise

        return query_results
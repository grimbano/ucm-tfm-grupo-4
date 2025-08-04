import psycopg2
from psycopg2.extras import RealDictCursor
import config

_DDL_COMMANDS = {
    'CREATE',
    'DROP',
    'ALTER'
}

_DML_COMMANDS = {
    'INSERT',
    'UPDATE',
    'DELETE'
}



def execute_commands(commands: list[str], port: int = None) -> None:
    """
    Execute a list of SQL DDL/DML commands against the database.

    This function takes a list of SQL commands and executes them sequentially
    against the database. It ensures that only valid DDL (Data Definition Language)
    and DML (Data Manipulation Language) commands are executed.

    Args:
        commands (list[str]): A list of SQL commands to execute. Each command
                              must be a valid DDL or DML command.
        port (int): An integer to force a different port that the .env one.

    Raises:
        AssertionError: If any command in the list is not a valid DDL or DML command.
        psycopg2.DatabaseError: If there is a database error during execution.
        Exception: For any other exceptions that occur during execution.

    Returns:
        None
    """

    not_valid_commands = len([
        True 
        for command in commands 
        if command.strip().upper().split()[0] not in _DDL_COMMANDS | _DML_COMMANDS
    ])

    assert not_valid_commands == 0, f'The commands list contains {not_valid_commands} invalid DDL/DML commands.'
    
    pg_config = config.get_pg_config()
    if port:
        pg_config['port'] = port

    try:
        with psycopg2.connect(**pg_config) as connection:
            with connection.cursor() as cursor:
                for command in commands:
                    cursor.execute(command)
                    print(f'\nThe following command was executed sucessfully:\n{command}')

    except (psycopg2.DatabaseError, Exception) as e:
        print(e)



def execute_query(query: str, port: int = None) -> list[dict] | None:
    """
    Executes a SQL SELECT query and returns the results as a list of dictionaries.

    Args:
        query (str): The SQL SELECT query to execute.

    Returns:
        list[dict] | None: A list of dictionaries representing the query results,
                           or None if the query fails.
        port (int): An integer to force a different port that the .env one.

    Raises:
        AssertionError: If the query is not a SELECT command.
        psycopg2.DatabaseError: If there is a database error.
        Exception: For any other exceptions that occur.
    """
    assert query.strip().upper().split()[0] in ('SELECT', 'WITH'), 'The query must be a `SELECT` command.'

    query_results = None
    pg_config = config.get_pg_config()
    if port:
        pg_config['port'] = port

    try:
        with psycopg2.connect(**pg_config) as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(query)
                query_results = cursor.fetchall()

    except (psycopg2.DatabaseError, Exception) as e:
        print(e)

    return query_results
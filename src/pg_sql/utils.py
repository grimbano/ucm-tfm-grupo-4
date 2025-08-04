def get_create_table_as(query: str, schema: str, table_name: str) -> str:
    """
    Generate a CREATE TABLE AS query.

    Args:
        query (str): The base query to create the table from.
        schema (str): The schema name for the new table.
        table_name (str): The name of the new table.

    Returns:
        str: The complete CREATE TABLE AS query.
    """
    create_table_as_query = []

    create_table_as_query.append(f'CREATE TABLE {schema}.{table_name} AS (')
    create_table_as_query.extend(query.replace(';', '').splitlines())
    create_table_as_query.append(');')
    
    return '\n'.join(create_table_as_query)
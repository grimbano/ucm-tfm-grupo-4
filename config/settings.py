
import dotenv
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class PostgresConfig(BaseSettings):
    """Represents the configuration for a PostgreSQL database.

    This class uses Pydantic to load and validate environment variables
    necessary for establishing a database connection.
    """
    POSTGRES_HOST: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_PORT: int = 5432
    
    model_config = SettingsConfigDict(
        env_file_encoding= 'utf-8',
        case_sensitive= True,
        extra= 'ignore'
    )
    
    def __init__(self, database_name: Optional[str] = None, **kwargs):
        """
        Initializes the PostgresConfig instance, allowing the database name
        to be passed as a parameter.
        
        Args:
            database_name (str, optional): The name of the database to connect to.
                If provided, it overrides the value from environment variables.
        """
        super().__init__(**kwargs)
        if database_name:
            self.POSTGRES_DB = database_name


    def get_db_uri(self, schema_name: str) -> str:
        """
        Generates the database URI string with a specified schema.

        Args:
            schema_name: The name of the schema to set in the search path.

        Returns:
            str: The formatted database URI.
        """
        if not schema_name:
            raise ValueError("A schema name must be provided to build the database URI.")

        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
            f"?options=-csearch_path%3D{schema_name}"
        )



def get_pg_config(
    env_file_path: Optional[str] = None,
    database_name: Optional[str] = None,
) -> PostgresConfig:
    """Initializes and returns the database configuration.

    Args:
        env_file_path: The path to a specific .env file.
                If not provided, Pydantic will automatically search for the file
                in the current directory and parent directories.
        database_name: The name of the database to connect to.
                If provided, it overrides the value from the .env file.

    Returns:
        PostgresConfig: A validated configuration object for the database.
    """
    env_file = env_file_path if env_file_path is not None else '.env'

    dotenv.load_dotenv(dotenv.find_dotenv(env_file, raise_error_if_not_found=True))

    return PostgresConfig(database_name=database_name, _env_file=env_file)


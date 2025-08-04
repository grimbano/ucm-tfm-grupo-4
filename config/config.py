
import os
import pathlib
import dotenv

_CONFIG_PARAM_HOST = 'host'
_CONFIG_PARAM_PORT = 'port'
_CONFIG_PARAM_DATABASE = 'database'
_CONFIG_PARAM_USER = 'user'
_CONFIG_PARAM_PASSWORD = 'password'



def get_pg_config(env_file: str = '../data/database/postgres/docker/.env') -> dict[str, str | int | None]:
    """
    Function to load and return the database configuration.
    """
    
    dotenv.load_dotenv(dotenv.find_dotenv(env_file, raise_error_if_not_found=True))

    config = {
        _CONFIG_PARAM_HOST: os.getenv('POSTGRES_HOST'),
        _CONFIG_PARAM_PORT: os.getenv('DB_PORT', 5432),
        _CONFIG_PARAM_DATABASE: os.getenv('POSTGRES_DB'),
        _CONFIG_PARAM_USER: os.getenv('POSTGRES_USER'),
        _CONFIG_PARAM_PASSWORD: os.getenv('POSTGRES_PASSWORD')
    }

    required_vars = [
        _CONFIG_PARAM_HOST, 
        _CONFIG_PARAM_DATABASE, 
        _CONFIG_PARAM_USER, 
        _CONFIG_PARAM_PASSWORD
    ]
    for var in required_vars:
        if config[var] is None:
            raise ValueError(f"Database environment variable '{var.upper()}' is not defined.")
            

    if isinstance(config['port'], str):
        try:
            config['port'] = int(config['port'])
        except ValueError:
            raise ValueError(f"Database port '{config['port']}' is not a valid number.")

    return config

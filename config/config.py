
import os
import pathlib
import dotenv

__CONFIG_PARAM_HOST = 'host'
__CONFIG_PARAM_PORT = 'port'
__CONFIG_PARAM_DATABASE = 'database'
__CONFIG_PARAM_USER = 'user'
__CONFIG_PARAM_PASSWORD = 'password'



def get_db_config(env_file: str = '../data/database/postgres/docker/.env') -> dict[str, str | int | None]:
    """
    Function to load and return the database configuration.
    """
    
    dotenv.load_dotenv(dotenv.find_dotenv(env_file, raise_error_if_not_found=True))

    config = {
        __CONFIG_PARAM_HOST: os.getenv('POSTGRES_HOST'),
        __CONFIG_PARAM_PORT: os.getenv('DB_PORT', 5432),
        __CONFIG_PARAM_DATABASE: os.getenv('POSTGRES_DB'),
        __CONFIG_PARAM_USER: os.getenv('POSTGRES_USER'),
        __CONFIG_PARAM_PASSWORD: os.getenv('POSTGRES_PASSWORD')
    }

    required_vars = [
        __CONFIG_PARAM_HOST, 
        __CONFIG_PARAM_DATABASE, 
        __CONFIG_PARAM_USER, 
        __CONFIG_PARAM_PASSWORD
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

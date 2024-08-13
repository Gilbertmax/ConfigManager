import json
import os
import logging
from functools import lru_cache, wraps

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

class ConfigError(Exception):
    """Excepción personalizada para errores de configuración."""
    pass

def validate_config(schema):
    """Decorador para validar configuraciones basado en un esquema."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            config = func(*args, **kwargs)
            for key, expected_type in schema.items():
                if key not in config:
                    raise ConfigError(f"Missing key in configuration: {key}")
                if not isinstance(config[key], expected_type):
                    raise ConfigError(f"Incorrect type for {key}: expected {expected_type}, got {type(config[key])}")
            logging.info(f"Configuration validated successfully against schema: {schema}")
            return config
        return wrapper
    return decorator

class ConfigLoader:
    """Clase para cargar configuraciones desde archivos JSON con caché."""
    
    def __init__(self, config_dir):
        self.config_dir = config_dir

    @lru_cache(maxsize=5)
    @validate_config(schema={"host": str, "port": int, "debug": bool})
    def load(self, config_name):
        """Carga una configuración desde un archivo JSON y la valida."""
        file_path = os.path.join(self.config_dir, f"{config_name}.json")
        
        if not os.path.exists(file_path):
            raise ConfigError(f"Configuration file not found: {file_path}")
        
        with open(file_path, 'r') as file:
            config = json.load(file)
        
        logging.info(f"Loaded configuration from {file_path}")
        return config

# Ejemplo de uso del sistema de configuración
if __name__ == "__main__":
    # Supongamos que tenemos un directorio 'configs' con archivos JSON
    config_dir = "configs"
    
    # Instanciamos el cargador de configuraciones
    config_loader = ConfigLoader(config_dir)
    
    try:
        # Cargamos y validamos una configuración
        app_config = config_loader.load("app_config")
        logging.info(f"App configuration: {app_config}")
        
        # Intentamos cargar la misma configuración para demostrar el uso de caché
        cached_config = config_loader.load("app_config")
        logging.info(f"Cached configuration: {cached_config}")

    except ConfigError as e:
        logging.error(f"Configuration error: {e}")

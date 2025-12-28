"""
Sistema de logging centralizado para la aplicación.
"""
import logging
import sys
from pathlib import Path
from config import LOG_LEVEL, LOG_FILE_FULL_PATH


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Configura y retorna un logger.
    
    Args:
        name: Nombre del logger
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    
    # Evitar duplicar handlers si ya está configurado
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Formato de los mensajes
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo
    try:
        LOG_FILE_FULL_PATH.parent.mkdir(exist_ok=True)
        file_handler = logging.FileHandler(LOG_FILE_FULL_PATH, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"No se pudo crear el archivo de log: {e}", file=sys.stderr)
    
    # Handler para consola (solo errores)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Logger por defecto
logger = setup_logger('seguro_complementario')

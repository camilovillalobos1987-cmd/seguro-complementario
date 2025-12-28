"""
Configuración centralizada de la aplicación.
Carga variables de entorno y define constantes.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Directorio base del proyecto
BASE_DIR = Path(__file__).resolve().parent

# Configuración de base de datos
DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/seguro_complementario.db')
DATABASE_FULL_PATH = BASE_DIR / DATABASE_PATH

# Configuración de la aplicación
APP_TITLE = os.getenv('APP_TITLE', 'Registro Seguro Complementario')
MAX_HIJOS = int(os.getenv('MAX_HIJOS', '10'))
EDAD_MAXIMA_HIJO = int(os.getenv('EDAD_MAXIMA_HIJO', '25'))

# Configuración de logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', 'data/app.log')
LOG_FILE_FULL_PATH = BASE_DIR / LOG_FILE

# Crear directorios necesarios
(BASE_DIR / 'data').mkdir(exist_ok=True)

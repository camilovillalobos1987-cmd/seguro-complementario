"""
Configuración centralizada de la aplicación.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Rutas de archivos
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
EXPORTS_DIR = BASE_DIR / "exports"

# Crear directorios si no existen
DATA_DIR.mkdir(exist_ok=True)
EXPORTS_DIR.mkdir(exist_ok=True)

# Configuración de base de datos
DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "seguro_complementario.db"))

# Configuración de la aplicación
APP_TITLE = os.getenv("APP_TITLE", "Registro Seguro Complementario")
MAX_HIJOS = int(os.getenv("MAX_HIJOS", "10"))
EDAD_MAXIMA_HIJO = int(os.getenv("EDAD_MAXIMA_HIJO", "25"))

# Configuración de logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", str(DATA_DIR / "app.log"))

# Configuración SMTP
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "")

# Contraseña de administrador
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin2024")

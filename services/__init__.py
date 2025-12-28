"""
Servicios de la aplicación.
"""
from .database import DatabaseService
from .email_service import enviar_correo_confirmacion, simular_envio_correo

# Bancos chilenos
BANCOS_CHILE = [
    "Banco de Chile",
    "Banco Estado",
    "Banco Santander",
    "BCI",
    "Banco Itaú",
    "Banco Scotiabank",
    "Banco BICE",
    "Banco Security",
    "Banco Falabella",
    "Banco Ripley",
    "Banco Consorcio",
    "Banco Internacional",
    "HSBC Bank",
    "JP Morgan Chase",
    "Otro"
]

# Tipos de cuenta
TIPOS_CUENTA = [
    "Cuenta Corriente",
    "Cuenta Vista",
    "Cuenta de Ahorro",
    "Cuenta RUT"
]

__all__ = [
    'DatabaseService',
    'BANCOS_CHILE',
    'TIPOS_CUENTA',
    'enviar_correo_confirmacion',
    'simular_envio_correo'
]

"""
Funciones de validación para datos del formulario.
Incluye validación de RUT chileno y otros campos.
"""
import re
from datetime import date


def limpiar_rut(rut: str) -> str:
    """
    Limpia el RUT removiendo puntos, guiones y espacios.
    
    Args:
        rut: RUT en cualquier formato
        
    Returns:
        RUT limpio (solo números y K)
    """
    return re.sub(r'[.\-\s]', '', rut.upper().strip())


def calcular_digito_verificador(rut_sin_dv: str) -> str:
    """
    Calcula el dígito verificador de un RUT chileno.
    
    Args:
        rut_sin_dv: RUT sin dígito verificador (solo números)
        
    Returns:
        Dígito verificador calculado (0-9 o K)
    """
    rut_reversed = rut_sin_dv[::-1]
    factors = [2, 3, 4, 5, 6, 7]
    suma = 0
    
    for i, digit in enumerate(rut_reversed):
        suma += int(digit) * factors[i % 6]
    
    resto = suma % 11
    dv = 11 - resto
    
    if dv == 11:
        return '0'
    elif dv == 10:
        return 'K'
    else:
        return str(dv)


def validar_rut(rut: str) -> tuple[bool, str]:
    """
    Valida un RUT chileno completo.
    
    Args:
        rut: RUT a validar (puede incluir puntos y guión)
        
    Returns:
        Tupla (es_valido, mensaje)
    """
    if not rut or not rut.strip():
        return False, "El RUT no puede estar vacío"
    
    rut_limpio = limpiar_rut(rut)
    
    # Validar formato básico
    if not re.match(r'^\d{7,8}[0-9K]$', rut_limpio):
        return False, "Formato de RUT inválido. Debe ser 12345678-9 o 12.345.678-9"
    
    # Separar número y dígito verificador
    rut_numero = rut_limpio[:-1]
    dv_ingresado = rut_limpio[-1]
    
    # Calcular dígito verificador correcto
    dv_calculado = calcular_digito_verificador(rut_numero)
    
    if dv_ingresado != dv_calculado:
        return False, f"RUT inválido. El dígito verificador debería ser {dv_calculado}"
    
    return True, "RUT válido"


def formatear_rut(rut: str) -> str:
    """
    Formatea un RUT al formato estándar 12.345.678-9
    
    Args:
        rut: RUT limpio o sin formatear
        
    Returns:
        RUT formateado
    """
    rut_limpio = limpiar_rut(rut)
    
    if len(rut_limpio) < 2:
        return rut
    
    rut_numero = rut_limpio[:-1]
    dv = rut_limpio[-1]
    
    # Agregar puntos cada 3 dígitos desde la derecha
    rut_formateado = ""
    for i, digit in enumerate(rut_numero[::-1]):
        if i > 0 and i % 3 == 0:
            rut_formateado = "." + rut_formateado
        rut_formateado = digit + rut_formateado
    
    return f"{rut_formateado}-{dv}"


def validar_nombre(nombre: str) -> tuple[bool, str]:
    """
    Valida que el nombre contenga solo caracteres válidos.
    
    Args:
        nombre: Nombre a validar
        
    Returns:
        Tupla (es_valido, mensaje)
    """
    if not nombre or not nombre.strip():
        return False, "El nombre no puede estar vacío"
    
    if len(nombre.strip()) < 2:
        return False, "El nombre debe tener al menos 2 caracteres"
    
    # Permitir letras, espacios, acentos, ñ, apóstrofes y guiones
    if not re.match(r"^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s'\-]+$", nombre):
        return False, "El nombre contiene caracteres no válidos"
    
    return True, "Nombre válido"


def calcular_edad(fecha_nacimiento: date) -> int:
    """
    Calcula la edad en años a partir de una fecha de nacimiento.
    
    Args:
        fecha_nacimiento: Fecha de nacimiento
        
    Returns:
        Edad en años
    """
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si aún no ha cumplido años este año
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    
    return edad


def validar_fecha_nacimiento(fecha_nacimiento: date, edad_maxima: int = None) -> tuple[bool, str]:
    """
    Valida que la fecha de nacimiento sea válida.
    
    Args:
        fecha_nacimiento: Fecha de nacimiento a validar
        edad_maxima: Edad máxima permitida (opcional)
        
    Returns:
        Tupla (es_valido, mensaje)
    """
    if fecha_nacimiento > date.today():
        return False, "La fecha de nacimiento no puede ser futura"
    
    edad = calcular_edad(fecha_nacimiento)
    
    if edad > 120:
        return False, "La edad calculada no es válida (mayor a 120 años)"
    
    if edad_maxima and edad > edad_maxima:
        return False, f"La edad ({edad} años) supera el máximo permitido ({edad_maxima} años)"
    
    return True, f"Fecha válida (edad: {edad} años)"


def validar_email(email: str) -> tuple[bool, str]:
    """
    Valida que el email tenga un formato correcto.
    
    Args:
        email: Email a validar
        
    Returns:
        Tupla (es_valido, mensaje)
    """
    if not email or not email.strip():
        return False, "El correo electrónico no puede estar vacío"
    
    email = email.strip().lower()
    
    # Patrón de email
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(patron, email):
        return False, "Formato de correo electrónico inválido"
    
    # Validar dominios comunes
    dominios_validos = ['.com', '.cl', '.net', '.org', '.edu', '.gov', '.io', '.co']
    tiene_dominio_valido = any(email.endswith(d) for d in dominios_validos)
    
    if not tiene_dominio_valido:
        return False, "El dominio del correo no parece válido"
    
    return True, "Correo electrónico válido"


def validar_numero_cuenta(numero: str) -> tuple[bool, str]:
    """
    Valida que el número de cuenta tenga un formato válido.
    
    Args:
        numero: Número de cuenta a validar
        
    Returns:
        Tupla (es_valido, mensaje)
    """
    if not numero or not numero.strip():
        return False, "El número de cuenta no puede estar vacío"
    
    # Remover espacios y guiones
    numero_limpio = re.sub(r'[\s\-]', '', numero)
    
    # Debe ser numérico y tener entre 5 y 20 dígitos
    if not numero_limpio.isdigit():
        return False, "El número de cuenta debe contener solo números"
    
    if len(numero_limpio) < 5 or len(numero_limpio) > 20:
        return False, "El número de cuenta debe tener entre 5 y 20 dígitos"
    
    return True, "Número de cuenta válido"

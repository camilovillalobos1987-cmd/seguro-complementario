"""
Tests unitarios para el módulo de validadores.
"""
import pytest
from datetime import date, timedelta
from utils.validators import (
    validar_rut,
    formatear_rut,
    limpiar_rut,
    calcular_digito_verificador,
    validar_nombre,
    validar_fecha_nacimiento,
    calcular_edad
)


class TestValidacionRUT:
    """Tests para validación de RUT chileno."""
    
    def test_rut_valido_con_formato(self):
        """Test RUT válido con formato estándar."""
        valido, mensaje = validar_rut("12.345.678-5")
        assert valido is True
        assert "válido" in mensaje.lower()
    
    def test_rut_valido_sin_formato(self):
        """Test RUT válido sin formato."""
        valido, mensaje = validar_rut("123456785")
        assert valido is True
    
    def test_rut_valido_con_k(self):
        """Test RUT válido con K como dígito verificador."""
        valido, mensaje = validar_rut("11.111.111-K")
        assert valido is True
    
    def test_rut_invalido_digito_verificador(self):
        """Test RUT con dígito verificador incorrecto."""
        valido, mensaje = validar_rut("12.345.678-9")
        assert valido is False
        assert "dígito verificador" in mensaje.lower()
    
    def test_rut_vacio(self):
        """Test RUT vacío."""
        valido, mensaje = validar_rut("")
        assert valido is False
        assert "vacío" in mensaje.lower()
    
    def test_rut_formato_invalido(self):
        """Test RUT con formato inválido."""
        valido, mensaje = validar_rut("123")
        assert valido is False
        assert "formato" in mensaje.lower()
    
    def test_limpiar_rut(self):
        """Test limpieza de RUT."""
        assert limpiar_rut("12.345.678-5") == "123456785"
        assert limpiar_rut("12345678-5") == "123456785"
        assert limpiar_rut("  12.345.678-5  ") == "123456785"
        assert limpiar_rut("12.345.678-k") == "123456785K"
    
    def test_formatear_rut(self):
        """Test formateo de RUT."""
        assert formatear_rut("123456785") == "12.345.678-5"
        assert formatear_rut("11111111K") == "11.111.111-K"
    
    def test_calcular_digito_verificador(self):
        """Test cálculo de dígito verificador."""
        assert calcular_digito_verificador("12345678") == "5"
        assert calcular_digito_verificador("11111111") == "K"
        assert calcular_digito_verificador("22222222") == "2"


class TestValidacionNombre:
    """Tests para validación de nombres."""
    
    def test_nombre_valido(self):
        """Test nombre válido."""
        valido, mensaje = validar_nombre("Juan Pérez")
        assert valido is True
    
    def test_nombre_con_acentos(self):
        """Test nombre con acentos y ñ."""
        valido, mensaje = validar_nombre("María José Núñez")
        assert valido is True
    
    def test_nombre_vacio(self):
        """Test nombre vacío."""
        valido, mensaje = validar_nombre("")
        assert valido is False
        assert "vacío" in mensaje.lower()
    
    def test_nombre_muy_corto(self):
        """Test nombre muy corto."""
        valido, mensaje = validar_nombre("A")
        assert valido is False
        assert "2 caracteres" in mensaje.lower()
    
    def test_nombre_con_numeros(self):
        """Test nombre con números."""
        valido, mensaje = validar_nombre("Juan123")
        assert valido is False
        assert "caracteres no válidos" in mensaje.lower()
    
    def test_nombre_con_apostrofe(self):
        """Test nombre con apóstrofe."""
        valido, mensaje = validar_nombre("O'Brien")
        assert valido is True


class TestValidacionFecha:
    """Tests para validación de fechas."""
    
    def test_fecha_valida(self):
        """Test fecha válida."""
        fecha = date(1990, 5, 15)
        valido, mensaje = validar_fecha_nacimiento(fecha)
        assert valido is True
    
    def test_fecha_futura(self):
        """Test fecha futura."""
        fecha = date.today() + timedelta(days=1)
        valido, mensaje = validar_fecha_nacimiento(fecha)
        assert valido is False
        assert "futura" in mensaje.lower()
    
    def test_edad_maxima(self):
        """Test validación de edad máxima."""
        # Fecha que da 26 años
        fecha = date.today() - timedelta(days=26*365 + 10)
        valido, mensaje = validar_fecha_nacimiento(fecha, edad_maxima=25)
        assert valido is False
        assert "supera el máximo" in mensaje.lower()
    
    def test_edad_muy_alta(self):
        """Test edad muy alta (más de 120 años)."""
        fecha = date(1800, 1, 1)
        valido, mensaje = validar_fecha_nacimiento(fecha)
        assert valido is False
        assert "120 años" in mensaje.lower()
    
    def test_calcular_edad(self):
        """Test cálculo de edad."""
        # Persona nacida hace exactamente 30 años
        fecha = date.today().replace(year=date.today().year - 30)
        edad = calcular_edad(fecha)
        assert edad == 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

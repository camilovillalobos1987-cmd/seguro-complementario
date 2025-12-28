"""
Servicio de envío de correos electrónicos.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from pathlib import Path
import os

from config import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, FROM_EMAIL, DATA_DIR
from utils.logger import logger


def calcular_fecha_alta(dias_habiles: int = 15) -> str:
    """Calcula la fecha de alta (15 días hábiles desde hoy)."""
    fecha = datetime.now()
    dias_agregados = 0
    
    while dias_agregados < dias_habiles:
        fecha += timedelta(days=1)
        if fecha.weekday() < 5:  # Lunes a viernes
            dias_agregados += 1
    
    return fecha.strftime("%d-%m-%Y")


def generar_html_confirmacion(datos_trabajador: dict, cargas: list) -> str:
    """Genera el HTML del correo de confirmación."""
    
    fecha_alta = calcular_fecha_alta()
    
    cargas_html = ""
    if cargas:
        cargas_html = "<h3>Cargas Familiares Registradas:</h3><ul>"
        for carga in cargas:
            cargas_html += f"<li><strong>{carga['tipo']}:</strong> {carga['nombre']} (RUT: {carga['rut']})</li>"
        cargas_html += "</ul>"
    else:
        cargas_html = "<p><em>No se registraron cargas familiares.</em></p>"
    
    banco_html = ""
    if datos_trabajador.get('banco'):
        banco_html = f"""
        <h3>Datos Bancarios:</h3>
        <ul>
            <li><strong>Banco:</strong> {datos_trabajador.get('banco')}</li>
            <li><strong>Tipo de Cuenta:</strong> {datos_trabajador.get('tipo_cuenta')}</li>
            <li><strong>Número de Cuenta:</strong> {datos_trabajador.get('numero_cuenta')}</li>
        </ul>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #1e3a5f 0%, #2e5984 100%); color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ background: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
            .info-box {{ background: #e8f4fd; border-left: 4px solid #1e3a5f; padding: 15px; margin: 15px 0; }}
            .footer {{ text-align: center; padding: 15px; font-size: 12px; color: #666; background: #f0f0f0; border-radius: 0 0 8px 8px; }}
            h3 {{ color: #1e3a5f; border-bottom: 2px solid #1e3a5f; padding-bottom: 5px; }}
            ul {{ background: white; padding: 15px 15px 15px 35px; border-radius: 5px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📋 Confirmación de Registro</h1>
            <p>Seguro Complementario</p>
        </div>
        
        <div class="content">
            <p>Estimado/a <strong>{datos_trabajador['nombre']}</strong>,</p>
            
            <p>Su registro en el Seguro Complementario ha sido recibido correctamente.</p>
            
            <div class="info-box">
                <strong>📅 Fecha estimada de alta:</strong> {fecha_alta}<br>
                <small>(15 días hábiles a partir de hoy)</small>
            </div>
            
            <h3>Datos del Trabajador:</h3>
            <ul>
                <li><strong>RUT:</strong> {datos_trabajador['rut']}</li>
                <li><strong>Nombre:</strong> {datos_trabajador['nombre']}</li>
                <li><strong>Email:</strong> {datos_trabajador['email']}</li>
            </ul>
            
            {banco_html}
            
            {cargas_html}
            
            <p><strong>Próximos pasos:</strong></p>
            <ol>
                <li>Guarde este correo como comprobante</li>
                <li>Su registro será procesado en los próximos días hábiles</li>
                <li>Si detecta algún error, contacte a Recursos Humanos</li>
            </ol>
        </div>
        
        <div class="footer">
            <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            <p>Sistema de Gestión de Seguro Complementario © {datetime.now().year}</p>
        </div>
    </body>
    </html>
    """
    
    return html


def enviar_correo_confirmacion(datos_trabajador: dict, cargas: list) -> bool:
    """Envía el correo de confirmación al trabajador."""
    
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("Configuración SMTP incompleta, simulando envío")
        return simular_envio_correo(datos_trabajador, cargas)
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "✅ Confirmación de Registro - Seguro Complementario"
        msg['From'] = FROM_EMAIL or SMTP_USER
        msg['To'] = datos_trabajador['email']
        
        html_content = generar_html_confirmacion(datos_trabajador, cargas)
        msg.attach(MIMEText(html_content, 'html'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Correo enviado a {datos_trabajador['email']}")
        return True
        
    except Exception as e:
        logger.error(f"Error al enviar correo: {e}")
        return simular_envio_correo(datos_trabajador, cargas)


def simular_envio_correo(datos_trabajador: dict, cargas: list) -> bool:
    """Simula el envío guardando el HTML localmente."""
    try:
        directorio = Path(DATA_DIR) / "correos_enviados"
        directorio.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rut_limpio = datos_trabajador['rut'].replace('.', '').replace('-', '')
        archivo = directorio / f"correo_{rut_limpio}_{timestamp}.html"
        
        html_content = generar_html_confirmacion(datos_trabajador, cargas)
        
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Correo simulado guardado en {archivo}")
        return True
        
    except Exception as e:
        logger.error(f"Error al simular correo: {e}")
        return False

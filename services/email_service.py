"""
Servicio de envío de correos electrónicos.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os

from utils.logger import logger


def calcular_fecha_alta(dias_habiles: int = 15) -> str:
    """
    Calcula la fecha estimada de alta considerando días hábiles.
    
    Args:
        dias_habiles: Número de días hábiles
        
    Returns:
        Fecha formateada
    """
    fecha = datetime.now()
    dias_agregados = 0
    
    while dias_agregados < dias_habiles:
        fecha += timedelta(days=1)
        # Saltar fines de semana (5=sábado, 6=domingo)
        if fecha.weekday() < 5:
            dias_agregados += 1
    
    return fecha.strftime("%d de %B de %Y")


def generar_html_confirmacion(registro: dict) -> str:
    """
    Genera el HTML del correo de confirmación.
    
    Args:
        registro: Diccionario con datos del registro y cargas
        
    Returns:
        HTML del correo
    """
    fecha_alta = calcular_fecha_alta(15)
    
    # Generar tabla de cargas
    cargas_html = ""
    if registro.get('cargas'):
        cargas_html = """
        <h3 style="color: #2c5aa0;">👨‍👩‍👧‍👦 Cargas Familiares Registradas</h3>
        <table style="width: 100%; border-collapse: collapse; margin: 20px 0;">
            <thead>
                <tr style="background-color: #2c5aa0; color: white;">
                    <th style="padding: 12px; text-align: left;">Tipo</th>
                    <th style="padding: 12px; text-align: left;">Nombre</th>
                    <th style="padding: 12px; text-align: left;">RUT</th>
                    <th style="padding: 12px; text-align: center;">Edad</th>
                </tr>
            </thead>
            <tbody>
        """
        for carga in registro['cargas']:
            cargas_html += f"""
                <tr style="border-bottom: 1px solid #ddd;">
                    <td style="padding: 12px;">{carga['tipo']}</td>
                    <td style="padding: 12px;">{carga['nombre']}</td>
                    <td style="padding: 12px;">{carga['rut']}</td>
                    <td style="padding: 12px; text-align: center;">{carga['edad']} años</td>
                </tr>
            """
        cargas_html += """
            </tbody>
        </table>
        """
    else:
        cargas_html = "<p><em>No se registraron cargas familiares.</em></p>"
    
    # Datos bancarios si existen
    banco_html = ""
    if registro.get('banco'):
        banco_html = f"""
        <h3 style="color: #2c5aa0;">🏦 Datos Bancarios Registrados</h3>
        <ul style="list-style: none; padding: 0;">
            <li><strong>Banco:</strong> {registro.get('banco', 'No especificado')}</li>
            <li><strong>Tipo de Cuenta:</strong> {registro.get('tipo_cuenta', 'No especificado')}</li>
            <li><strong>Número de Cuenta:</strong> {registro.get('numero_cuenta', 'No especificado')}</li>
        </ul>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .header {{
                background: linear-gradient(135deg, #2c5aa0, #1e3c72);
                color: white;
                padding: 30px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            .content {{
                background: #f9f9f9;
                padding: 30px;
                border: 1px solid #ddd;
            }}
            .footer {{
                background: #2c5aa0;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 0 0 10px 10px;
                font-size: 0.9em;
            }}
            .highlight {{
                background: #e8f4f8;
                padding: 15px;
                border-left: 4px solid #2c5aa0;
                margin: 20px 0;
            }}
            .success-badge {{
                display: inline-block;
                background: #28a745;
                color: white;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📋 Seguro Complementario</h1>
            <p>Confirmación de Registro</p>
        </div>
        
        <div class="content">
            <p>Estimado/a <strong>{registro['nombre_trabajador']}</strong>,</p>
            
            <p>
                <span class="success-badge">✅ Registro Exitoso</span>
            </p>
            
            <p>Le informamos que su solicitud de inscripción al Seguro Complementario 
            ha sido recibida correctamente.</p>
            
            <div class="highlight">
                <strong>📅 Fecha estimada de alta:</strong><br>
                Sus cargas familiares estarán habilitadas en el seguro dentro de 
                <strong>15 días hábiles</strong>, aproximadamente el <strong>{fecha_alta}</strong>.
            </div>
            
            <h3 style="color: #2c5aa0;">📝 Datos del Titular</h3>
            <ul style="list-style: none; padding: 0;">
                <li><strong>Nombre:</strong> {registro['nombre_trabajador']}</li>
                <li><strong>RUT:</strong> {registro['rut_trabajador']}</li>
                <li><strong>Email:</strong> {registro['email']}</li>
            </ul>
            
            {cargas_html}
            
            {banco_html}
            
            <div class="highlight">
                <strong>📌 Importante:</strong><br>
                <ul>
                    <li>Guarde este correo como comprobante de su registro.</li>
                    <li>Si detecta algún error en los datos, comuníquese con Recursos Humanos.</li>
                    <li>Recibirá la póliza de seguro una vez que el proceso esté completado.</li>
                </ul>
            </div>
            
            <p>Si tiene alguna consulta, no dude en contactarnos.</p>
            
            <p>Atentamente,<br>
            <strong>Departamento de Recursos Humanos</strong></p>
        </div>
        
        <div class="footer">
            <p>Este es un correo automático, por favor no responda a este mensaje.</p>
            <p>© {datetime.now().year} - Seguro Complementario</p>
        </div>
    </body>
    </html>
    """
    
    return html


def enviar_correo_confirmacion(registro: dict) -> tuple[bool, str]:
    """
    Envía correo de confirmación al trabajador.
    
    Args:
        registro: Diccionario con datos del registro
        
    Returns:
        Tupla (exitoso, mensaje)
    """
    # Configuración SMTP desde variables de entorno
    smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_user = os.getenv('SMTP_USER', '')
    smtp_password = os.getenv('SMTP_PASSWORD', '')
    from_email = os.getenv('FROM_EMAIL', smtp_user)
    
    # Verificar configuración
    if not smtp_user or not smtp_password:
        logger.warning("Configuración SMTP no disponible. Email no enviado.")
        return False, "Configuración de correo no disponible. Contacte al administrador."
    
    try:
        # Crear mensaje
        msg = MIMEMultipart('alternative')
        msg['Subject'] = '✅ Confirmación de Registro - Seguro Complementario'
        msg['From'] = from_email
        msg['To'] = registro['email']
        
        # Generar contenido HTML
        html_content = generar_html_confirmacion(registro)
        
        # Versión texto plano
        text_content = f"""
        Confirmación de Registro - Seguro Complementario
        
        Estimado/a {registro['nombre_trabajador']},
        
        Su solicitud de inscripción al Seguro Complementario ha sido recibida correctamente.
        
        Fecha estimada de alta: 15 días hábiles aproximadamente.
        
        Datos registrados:
        - Nombre: {registro['nombre_trabajador']}
        - RUT: {registro['rut_trabajador']}
        - Email: {registro['email']}
        
        Total de cargas registradas: {len(registro.get('cargas', []))}
        
        Guarde este correo como comprobante.
        
        Atentamente,
        Departamento de Recursos Humanos
        """
        
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Enviar
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        
        logger.info(f"Correo enviado exitosamente a {registro['email']}")
        return True, "Correo de confirmación enviado exitosamente"
        
    except smtplib.SMTPAuthenticationError:
        logger.error("Error de autenticación SMTP")
        return False, "Error de autenticación del servidor de correo"
    except smtplib.SMTPException as e:
        logger.error(f"Error SMTP: {e}")
        return False, f"Error al enviar correo: {str(e)}"
    except Exception as e:
        logger.error(f"Error inesperado al enviar correo: {e}")
        return False, f"Error inesperado: {str(e)}"


def simular_envio_correo(registro: dict) -> tuple[bool, str]:
    """
    Simula el envío de correo (para cuando no hay SMTP configurado).
    Guarda el correo como archivo HTML.
    
    Args:
        registro: Diccionario con datos del registro
        
    Returns:
        Tupla (exitoso, mensaje)
    """
    try:
        from pathlib import Path
        
        # Crear directorio de correos
        correos_dir = Path("data/correos_enviados")
        correos_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        rut_limpio = registro['rut_trabajador'].replace('.', '').replace('-', '')
        archivo = correos_dir / f"correo_{rut_limpio}_{timestamp}.html"
        
        # Guardar HTML
        html_content = generar_html_confirmacion(registro)
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Correo simulado guardado en {archivo}")
        return True, f"Correo guardado en: {archivo}"
        
    except Exception as e:
        logger.error(f"Error al simular correo: {e}")
        return False, f"Error: {str(e)}"

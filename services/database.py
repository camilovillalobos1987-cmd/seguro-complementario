"""
Servicio de base de datos SQLite para gestionar empleados y cargas familiares.
"""
import sqlite3
from datetime import date, datetime
from typing import List, Dict, Optional
from pathlib import Path
import pandas as pd

from config import DATABASE_FULL_PATH
from utils.logger import logger


# Lista de bancos chilenos
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
    "Coopeuch",
    "Banco Internacional",
    "HSBC Bank",
    "Otro"
]

# Tipos de cuenta
TIPOS_CUENTA = [
    "Cuenta Corriente",
    "Cuenta Vista",
    "Cuenta de Ahorro",
    "Cuenta RUT"
]


class DatabaseService:
    """Servicio para gestionar la base de datos de empleados y cargas familiares."""
    
    def __init__(self, db_path: Path = DATABASE_FULL_PATH):
        """
        Inicializa el servicio de base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos
        """
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Crea las tablas si no existen."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla de empleados de la empresa (para validación)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS empleados (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rut TEXT UNIQUE NOT NULL,
                        nombre TEXT NOT NULL,
                        email TEXT,
                        activo BOOLEAN DEFAULT 1,
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Tabla de registros del trabajador (formulario completado)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS registros_trabajador (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        rut_trabajador TEXT NOT NULL,
                        nombre_trabajador TEXT NOT NULL,
                        email TEXT NOT NULL,
                        banco TEXT,
                        tipo_cuenta TEXT,
                        numero_cuenta TEXT,
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        email_enviado BOOLEAN DEFAULT 0,
                        activo BOOLEAN DEFAULT 1,
                        fecha_baja TIMESTAMP,
                        motivo_baja TEXT,
                        FOREIGN KEY (rut_trabajador) REFERENCES empleados(rut)
                    )
                """)
                
                # Tabla de cargas familiares (vinculada al registro)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cargas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        registro_id INTEGER NOT NULL,
                        tipo TEXT NOT NULL,
                        rut TEXT NOT NULL,
                        nombre TEXT NOT NULL,
                        fecha_nacimiento DATE NOT NULL,
                        edad INTEGER NOT NULL,
                        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        activo BOOLEAN DEFAULT 1,
                        fecha_eliminacion TIMESTAMP,
                        FOREIGN KEY (registro_id) REFERENCES registros_trabajador(id)
                    )
                """)
                
                # Tabla de notificaciones para el administrador
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notificaciones_admin (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        tipo TEXT NOT NULL,
                        rut_trabajador TEXT NOT NULL,
                        nombre_trabajador TEXT NOT NULL,
                        descripcion TEXT NOT NULL,
                        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        leida BOOLEAN DEFAULT 0
                    )
                """)
                
                # Índices para mejorar rendimiento
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_empleados_rut 
                    ON empleados(rut)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_registros_rut 
                    ON registros_trabajador(rut_trabajador)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_cargas_registro 
                    ON cargas(registro_id)
                """)
                
                # Migrar tablas existentes agregando columnas si no existen
                try:
                    cursor.execute("ALTER TABLE registros_trabajador ADD COLUMN activo BOOLEAN DEFAULT 1")
                except: pass
                try:
                    cursor.execute("ALTER TABLE registros_trabajador ADD COLUMN fecha_baja TIMESTAMP")
                except: pass
                try:
                    cursor.execute("ALTER TABLE registros_trabajador ADD COLUMN motivo_baja TEXT")
                except: pass
                try:
                    cursor.execute("ALTER TABLE cargas ADD COLUMN activo BOOLEAN DEFAULT 1")
                except: pass
                try:
                    cursor.execute("ALTER TABLE cargas ADD COLUMN fecha_eliminacion TIMESTAMP")
                except: pass
                
                conn.commit()
                logger.info(f"Base de datos inicializada en {self.db_path}")
        except Exception as e:
            logger.error(f"Error al inicializar base de datos: {e}")
            raise
    
    # ==================== GESTIÓN DE EMPLEADOS ====================
    
    def agregar_empleado(self, rut: str, nombre: str, email: str = None) -> bool:
        """
        Agrega un nuevo empleado a la base de datos.
        
        Args:
            rut: RUT del empleado
            nombre: Nombre completo
            email: Correo electrónico (opcional)
            
        Returns:
            True si se agregó exitosamente
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO empleados (rut, nombre, email)
                    VALUES (?, ?, ?)
                """, (rut, nombre, email))
                conn.commit()
                logger.info(f"Empleado agregado: {nombre} (RUT: {rut})")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Empleado ya existe: RUT {rut}")
            return False
        except Exception as e:
            logger.error(f"Error al agregar empleado: {e}")
            return False
    
    def verificar_empleado_existe(self, rut: str) -> tuple[bool, Optional[Dict]]:
        """
        Verifica si un empleado está registrado en la empresa.
        
        Args:
            rut: RUT a verificar
            
        Returns:
            Tupla (existe, datos_empleado)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM empleados 
                    WHERE rut = ? AND activo = 1
                """, (rut,))
                
                row = cursor.fetchone()
                if row:
                    return True, dict(row)
                return False, None
        except Exception as e:
            logger.error(f"Error al verificar empleado: {e}")
            return False, None
    
    def obtener_todos_empleados(self) -> List[Dict]:
        """Obtiene todos los empleados activos."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM empleados 
                    WHERE activo = 1
                    ORDER BY nombre
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener empleados: {e}")
            return []
    
    def importar_empleados_excel(self, archivo: str) -> tuple[int, int]:
        """
        Importa empleados desde un archivo Excel.
        
        Args:
            archivo: Ruta al archivo Excel
            
        Returns:
            Tupla (exitosos, fallidos)
        """
        try:
            df = pd.read_excel(archivo)
            exitosos = 0
            fallidos = 0
            
            for _, row in df.iterrows():
                rut = str(row.get('RUT', row.get('rut', ''))).strip()
                nombre = str(row.get('Nombre', row.get('nombre', ''))).strip()
                email = str(row.get('Email', row.get('email', ''))).strip() if 'Email' in row or 'email' in row else None
                
                if rut and nombre:
                    if self.agregar_empleado(rut, nombre, email):
                        exitosos += 1
                    else:
                        fallidos += 1
                else:
                    fallidos += 1
            
            logger.info(f"Importación completada: {exitosos} exitosos, {fallidos} fallidos")
            return exitosos, fallidos
        except Exception as e:
            logger.error(f"Error al importar empleados: {e}")
            return 0, 0
    
    # ==================== GESTIÓN DE REGISTROS ====================
    
    def crear_registro_trabajador(
        self,
        rut_trabajador: str,
        nombre_trabajador: str,
        email: str,
        banco: str = None,
        tipo_cuenta: str = None,
        numero_cuenta: str = None
    ) -> Optional[int]:
        """
        Crea un nuevo registro de trabajador.
        
        Returns:
            ID del registro creado o None si falló
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO registros_trabajador 
                    (rut_trabajador, nombre_trabajador, email, banco, tipo_cuenta, numero_cuenta)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (rut_trabajador, nombre_trabajador, email, banco, tipo_cuenta, numero_cuenta))
                conn.commit()
                
                registro_id = cursor.lastrowid
                logger.info(f"Registro creado: ID {registro_id} para {nombre_trabajador}")
                return registro_id
        except Exception as e:
            logger.error(f"Error al crear registro: {e}")
            return None
    
    def agregar_carga_a_registro(
        self,
        registro_id: int,
        tipo: str,
        rut: str,
        nombre: str,
        fecha_nacimiento: date,
        edad: int
    ) -> bool:
        """
        Agrega una carga familiar a un registro existente.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cargas (registro_id, tipo, rut, nombre, fecha_nacimiento, edad)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (registro_id, tipo, rut, nombre, fecha_nacimiento.isoformat(), edad))
                conn.commit()
                
                logger.info(f"Carga agregada al registro {registro_id}: {tipo} - {nombre}")
                return True
        except Exception as e:
            logger.error(f"Error al agregar carga: {e}")
            return False
    
    def obtener_registro_con_cargas(self, registro_id: int) -> Optional[Dict]:
        """
        Obtiene un registro completo con todas sus cargas.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Obtener registro
                cursor.execute("""
                    SELECT * FROM registros_trabajador WHERE id = ?
                """, (registro_id,))
                registro = cursor.fetchone()
                
                if not registro:
                    return None
                
                registro_dict = dict(registro)
                
                # Obtener cargas
                cursor.execute("""
                    SELECT * FROM cargas WHERE registro_id = ? ORDER BY tipo, nombre
                """, (registro_id,))
                cargas = [dict(row) for row in cursor.fetchall()]
                
                registro_dict['cargas'] = cargas
                return registro_dict
        except Exception as e:
            logger.error(f"Error al obtener registro: {e}")
            return None
    
    def marcar_email_enviado(self, registro_id: int) -> bool:
        """Marca un registro como con email enviado."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE registros_trabajador 
                    SET email_enviado = 1 
                    WHERE id = ?
                """, (registro_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error al actualizar estado de email: {e}")
            return False
    
    # ==================== PANEL ADMINISTRADOR ====================
    
    def obtener_todos_registros(self) -> List[Dict]:
        """Obtiene todos los registros con sus cargas para el administrador."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT r.*, 
                           COUNT(c.id) as total_cargas,
                           GROUP_CONCAT(c.nombre, ', ') as nombres_cargas
                    FROM registros_trabajador r
                    LEFT JOIN cargas c ON r.id = c.registro_id
                    GROUP BY r.id
                    ORDER BY r.fecha_registro DESC
                """)
                
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener registros: {e}")
            return []
    
    def exportar_registros_excel(self, archivo_salida: str = "exports/registros_seguro.xlsx") -> bool:
        """
        Exporta todos los registros a Excel para enviar al seguro.
        """
        try:
            Path(archivo_salida).parent.mkdir(exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                # Datos de registros
                df_registros = pd.read_sql_query("""
                    SELECT 
                        rut_trabajador as 'RUT Trabajador',
                        nombre_trabajador as 'Nombre Trabajador',
                        email as 'Email',
                        banco as 'Banco',
                        tipo_cuenta as 'Tipo Cuenta',
                        numero_cuenta as 'Número Cuenta',
                        fecha_registro as 'Fecha Registro'
                    FROM registros_trabajador
                    ORDER BY fecha_registro DESC
                """, conn)
                
                # Datos de cargas con datos bancarios del trabajador
                df_cargas = pd.read_sql_query("""
                    SELECT 
                        r.rut_trabajador as 'RUT Trabajador',
                        r.nombre_trabajador as 'Nombre Trabajador',
                        r.email as 'Email Trabajador',
                        r.banco as 'Banco',
                        r.tipo_cuenta as 'Tipo Cuenta',
                        r.numero_cuenta as 'Número Cuenta',
                        c.tipo as 'Tipo Carga',
                        c.rut as 'RUT Carga',
                        c.nombre as 'Nombre Carga',
                        c.fecha_nacimiento as 'Fecha Nacimiento',
                        c.edad as 'Edad'
                    FROM cargas c
                    JOIN registros_trabajador r ON c.registro_id = r.id
                    ORDER BY r.nombre_trabajador, c.tipo
                """, conn)
            
            # Escribir en Excel con múltiples hojas
            with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
                # Convertir fechas a formato chileno DD-MM-YY
                if 'Fecha Registro' in df_registros.columns:
                    df_registros['Fecha Registro'] = pd.to_datetime(df_registros['Fecha Registro']).dt.strftime('%d-%m-%y')
                
                if 'Fecha Nacimiento' in df_cargas.columns:
                    df_cargas['Fecha Nacimiento'] = pd.to_datetime(df_cargas['Fecha Nacimiento']).dt.strftime('%d-%m-%y')
                
                df_registros.to_excel(writer, sheet_name='Trabajadores', index=False)
                df_cargas.to_excel(writer, sheet_name='Cargas Familiares', index=False)
            
            logger.info(f"Registros exportados a {archivo_salida}")
            return True
        except Exception as e:
            logger.error(f"Error al exportar: {e}")
            return False
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas para el dashboard."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT COUNT(*) FROM empleados WHERE activo = 1")
                total_empleados = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM registros_trabajador")
                total_registros = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM cargas")
                total_cargas = cursor.fetchone()[0]
                
                cursor.execute("""
                    SELECT tipo, COUNT(*) FROM cargas GROUP BY tipo
                """)
                cargas_por_tipo = dict(cursor.fetchall())
                
                cursor.execute("""
                    SELECT COUNT(*) FROM registros_trabajador WHERE email_enviado = 1
                """)
                emails_enviados = cursor.fetchone()[0]
                
                return {
                    'total_empleados': total_empleados,
                    'total_registros': total_registros,
                    'total_cargas': total_cargas,
                    'cargas_por_tipo': cargas_por_tipo,
                    'emails_enviados': emails_enviados
                }
        except Exception as e:
            logger.error(f"Error al obtener estadísticas: {e}")
            return {}
    
    # ==================== PORTAL DE AUTOSERVICIO ====================
    
    def obtener_registro_por_rut(self, rut_trabajador: str) -> Optional[Dict]:
        """
        Obtiene el registro activo de un trabajador por su RUT.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM registros_trabajador 
                    WHERE rut_trabajador = ? AND activo = 1
                    ORDER BY fecha_registro DESC
                    LIMIT 1
                """, (rut_trabajador,))
                
                row = cursor.fetchone()
                if row:
                    registro = dict(row)
                    # Obtener cargas activas
                    cursor.execute("""
                        SELECT * FROM cargas 
                        WHERE registro_id = ? AND activo = 1
                        ORDER BY tipo, nombre
                    """, (registro['id'],))
                    registro['cargas'] = [dict(r) for r in cursor.fetchall()]
                    return registro
                return None
        except Exception as e:
            logger.error(f"Error al obtener registro por RUT: {e}")
            return None
    
    def eliminar_carga(self, carga_id: int, rut_trabajador: str, nombre_trabajador: str) -> bool:
        """
        Marca una carga como eliminada y notifica al admin.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Obtener datos de la carga antes de eliminar
                cursor.execute("SELECT tipo, nombre, rut FROM cargas WHERE id = ?", (carga_id,))
                carga = cursor.fetchone()
                
                if not carga:
                    return False
                
                # Marcar como inactiva
                cursor.execute("""
                    UPDATE cargas 
                    SET activo = 0, fecha_eliminacion = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (carga_id,))
                
                # Crear notificación para admin
                descripcion = f"Eliminó carga: {carga[0]} - {carga[1]} (RUT: {carga[2]})"
                cursor.execute("""
                    INSERT INTO notificaciones_admin 
                    (tipo, rut_trabajador, nombre_trabajador, descripcion)
                    VALUES ('ELIMINACION_CARGA', ?, ?, ?)
                """, (rut_trabajador, nombre_trabajador, descripcion))
                
                conn.commit()
                logger.info(f"Carga {carga_id} eliminada por {nombre_trabajador}")
                return True
        except Exception as e:
            logger.error(f"Error al eliminar carga: {e}")
            return False
    
    def dar_baja_seguro(self, registro_id: int, rut_trabajador: str, nombre_trabajador: str, motivo: str = "Solicitud del trabajador") -> bool:
        """
        Da de baja el seguro de un trabajador.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Marcar registro como inactivo
                cursor.execute("""
                    UPDATE registros_trabajador 
                    SET activo = 0, fecha_baja = CURRENT_TIMESTAMP, motivo_baja = ?
                    WHERE id = ?
                """, (motivo, registro_id))
                
                # Marcar todas las cargas como inactivas
                cursor.execute("""
                    UPDATE cargas 
                    SET activo = 0, fecha_eliminacion = CURRENT_TIMESTAMP
                    WHERE registro_id = ?
                """, (registro_id,))
                
                # Crear notificación para admin
                cursor.execute("""
                    INSERT INTO notificaciones_admin 
                    (tipo, rut_trabajador, nombre_trabajador, descripcion)
                    VALUES ('BAJA_SEGURO', ?, ?, ?)
                """, (rut_trabajador, nombre_trabajador, f"Solicitó BAJA del seguro. Motivo: {motivo}"))
                
                conn.commit()
                logger.info(f"Baja de seguro procesada para {nombre_trabajador}")
                return True
        except Exception as e:
            logger.error(f"Error al dar de baja: {e}")
            return False
    
    def obtener_notificaciones_pendientes(self) -> List[Dict]:
        """
        Obtiene las notificaciones pendientes para el administrador.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM notificaciones_admin 
                    WHERE leida = 0
                    ORDER BY fecha DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener notificaciones: {e}")
            return []
    
    def marcar_notificacion_leida(self, notificacion_id: int) -> bool:
        """Marca una notificación como leída."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE notificaciones_admin SET leida = 1 WHERE id = ?
                """, (notificacion_id,))
                conn.commit()
                return True
        except:
            return False
    
    def marcar_todas_notificaciones_leidas(self) -> bool:
        """Marca todas las notificaciones como leídas."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE notificaciones_admin SET leida = 1")
                conn.commit()
                return True
        except:
            return False

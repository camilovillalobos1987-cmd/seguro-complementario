"""
Servicio de base de datos SQLite para el sistema de seguro complementario.
"""
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import pandas as pd
import os

from config import DATABASE_PATH, EXPORTS_DIR
from utils.logger import logger


class DatabaseService:
    """Servicio de gestión de base de datos SQLite."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        # Crear directorio si no existe
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
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
                
                # Tabla de registros del trabajador
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
                        enviado_aseguradora BOOLEAN DEFAULT 0,
                        fecha_envio_aseguradora TIMESTAMP,
                        numero_lote TEXT,
                        FOREIGN KEY (rut_trabajador) REFERENCES empleados(rut)
                    )
                """)
                
                # Tabla de cargas familiares
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
                        enviado_aseguradora BOOLEAN DEFAULT 0,
                        fecha_envio_aseguradora TIMESTAMP,
                        numero_lote TEXT,
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
                
                # Índices
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_empleados_rut ON empleados(rut)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_registros_rut ON registros_trabajador(rut_trabajador)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_cargas_registro ON cargas(registro_id)")
                
                conn.commit()
                logger.info(f"Base de datos inicializada en {self.db_path}")
        except Exception as e:
            logger.error(f"Error al inicializar base de datos: {e}")
            raise
    
    # ==================== GESTIÓN DE EMPLEADOS ====================
    
    def agregar_empleado(self, rut: str, nombre: str, email: str = None) -> bool:
        """Agrega un nuevo empleado a la base de datos."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO empleados (rut, nombre, email) VALUES (?, ?, ?)",
                    (rut, nombre, email)
                )
                conn.commit()
                logger.info(f"Empleado agregado: {nombre}")
                return True
        except sqlite3.IntegrityError:
            logger.warning(f"Empleado ya existe: {rut}")
            return False
        except Exception as e:
            logger.error(f"Error al agregar empleado: {e}")
            return False
    
    def verificar_empleado_existe(self, rut: str) -> Tuple[bool, Optional[Dict]]:
        """Verifica si un empleado existe y retorna sus datos."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM empleados WHERE rut = ? AND activo = 1",
                    (rut,)
                )
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
                cursor.execute("SELECT * FROM empleados WHERE activo = 1 ORDER BY nombre")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener empleados: {e}")
            return []
    
    def importar_empleados_excel(self, archivo_path: str) -> Tuple[int, int, str]:
        """
        Importa empleados desde un archivo Excel.
        
        Returns:
            Tuple[int, int, str]: (exitosos, fallidos, mensaje_error)
        """
        try:
            df = pd.read_excel(archivo_path)
            
            # Verificar que hay datos
            if df.empty:
                return 0, 0, "El archivo está vacío"
            
            # Verificar columnas requeridas
            columnas = [col.lower() for col in df.columns]
            if 'rut' not in columnas and 'RUT' not in df.columns:
                return 0, 0, "El archivo no tiene columna 'RUT'"
            if 'nombre' not in columnas and 'Nombre' not in df.columns:
                return 0, 0, "El archivo no tiene columna 'Nombre'"
            
            exitosos = 0
            fallidos = 0
            errores = []
            
            for idx, row in df.iterrows():
                rut = str(row.get('RUT', row.get('rut', ''))).strip()
                nombre = str(row.get('Nombre', row.get('nombre', ''))).strip()
                email = None
                if 'Email' in row:
                    email = str(row.get('Email', '')).strip()
                elif 'email' in row:
                    email = str(row.get('email', '')).strip()
                
                # Limpiar valores nan
                if rut == 'nan':
                    rut = ''
                if nombre == 'nan':
                    nombre = ''
                if email == 'nan':
                    email = None
                
                if rut and nombre:
                    if self.agregar_empleado(rut, nombre, email):
                        exitosos += 1
                    else:
                        fallidos += 1
                        errores.append(f"Fila {idx+2}: RUT {rut} ya existe o es inválido")
                else:
                    fallidos += 1
                    errores.append(f"Fila {idx+2}: RUT o Nombre vacío")
            
            error_msg = "; ".join(errores[:5]) if errores else ""  # Mostrar máx 5 errores
            if len(errores) > 5:
                error_msg += f" ... y {len(errores)-5} más"
            
            return exitosos, fallidos, error_msg
            
        except Exception as e:
            logger.error(f"Error al importar empleados: {e}")
            return 0, 0, str(e)
    
    # ==================== GESTIÓN DE REGISTROS ====================
    
    def crear_registro_trabajador(self, rut: str, nombre: str, email: str,
                                   banco: str = None, tipo_cuenta: str = None,
                                   numero_cuenta: str = None) -> Optional[int]:
        """Crea un nuevo registro de trabajador."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO registros_trabajador 
                    (rut_trabajador, nombre_trabajador, email, banco, tipo_cuenta, numero_cuenta)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (rut, nombre, email, banco, tipo_cuenta, numero_cuenta))
                conn.commit()
                registro_id = cursor.lastrowid
                logger.info(f"Registro creado: {nombre} (ID: {registro_id})")
                return registro_id
        except Exception as e:
            logger.error(f"Error al crear registro: {e}")
            return None
    
    def agregar_carga_a_registro(self, registro_id: int, tipo: str, rut: str,
                                  nombre: str, fecha_nacimiento, edad: int) -> bool:
        """Agrega una carga familiar a un registro."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO cargas (registro_id, tipo, rut, nombre, fecha_nacimiento, edad)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (registro_id, tipo, rut, nombre, fecha_nacimiento, edad))
                conn.commit()
                logger.info(f"Carga agregada: {nombre}")
                return True
        except Exception as e:
            logger.error(f"Error al agregar carga: {e}")
            return False
    
    def obtener_registro_con_cargas(self, registro_id: int) -> Optional[Dict]:
        """Obtiene un registro con sus cargas."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute("SELECT * FROM registros_trabajador WHERE id = ?", (registro_id,))
                registro = cursor.fetchone()
                
                if registro:
                    registro = dict(registro)
                    cursor.execute(
                        "SELECT * FROM cargas WHERE registro_id = ? AND activo = 1",
                        (registro_id,)
                    )
                    registro['cargas'] = [dict(row) for row in cursor.fetchall()]
                    return registro
                return None
        except Exception as e:
            logger.error(f"Error al obtener registro: {e}")
            return None
    
    def marcar_email_enviado(self, registro_id: int) -> bool:
        """Marca un registro como email enviado."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE registros_trabajador SET email_enviado = 1 WHERE id = ?",
                    (registro_id,)
                )
                conn.commit()
                return True
        except:
            return False
    
    # ==================== ADMINISTRACIÓN ====================
    
    def obtener_todos_registros(self) -> List[Dict]:
        """Obtiene todos los registros para el administrador."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT r.*, 
                           GROUP_CONCAT(c.nombre || ' (' || c.tipo || ')') as nombres_cargas
                    FROM registros_trabajador r
                    LEFT JOIN cargas c ON r.id = c.registro_id AND c.activo = 1
                    WHERE r.activo = 1
                    GROUP BY r.id
                    ORDER BY r.fecha_registro DESC
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener registros: {e}")
            return []
    
    def exportar_registros_excel(self, archivo_salida: str = None) -> bool:
        """Exporta registros a Excel."""
        try:
            if not archivo_salida:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo_salida = str(EXPORTS_DIR / f"registros_{timestamp}.xlsx")
            
            Path(archivo_salida).parent.mkdir(parents=True, exist_ok=True)
            
            with sqlite3.connect(self.db_path) as conn:
                df_registros = pd.read_sql_query("""
                    SELECT 
                        rut_trabajador as 'RUT',
                        nombre_trabajador as 'Nombre',
                        email as 'Email',
                        banco as 'Banco',
                        tipo_cuenta as 'Tipo Cuenta',
                        numero_cuenta as 'Número Cuenta',
                        fecha_registro as 'Fecha Registro'
                    FROM registros_trabajador
                    WHERE activo = 1
                    ORDER BY fecha_registro DESC
                """, conn)
                
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
                    WHERE c.activo = 1 AND r.activo = 1
                    ORDER BY r.nombre_trabajador, c.tipo
                """, conn)
            
            with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
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
                
                cursor.execute("SELECT COUNT(*) FROM registros_trabajador WHERE activo = 1")
                total_registros = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM cargas WHERE activo = 1")
                total_cargas = cursor.fetchone()[0]
                
                cursor.execute("SELECT tipo, COUNT(*) FROM cargas WHERE activo = 1 GROUP BY tipo")
                cargas_por_tipo = dict(cursor.fetchall())
                
                cursor.execute("SELECT COUNT(*) FROM registros_trabajador WHERE email_enviado = 1")
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
        """Obtiene el registro activo de un trabajador por su RUT."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM registros_trabajador 
                    WHERE rut_trabajador = ? AND activo = 1
                    ORDER BY fecha_registro DESC LIMIT 1
                """, (rut_trabajador,))
                
                row = cursor.fetchone()
                if row:
                    registro = dict(row)
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
        """Marca una carga como eliminada y notifica al admin."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("SELECT tipo, nombre, rut FROM cargas WHERE id = ?", (carga_id,))
                carga = cursor.fetchone()
                
                if not carga:
                    return False
                
                cursor.execute("""
                    UPDATE cargas SET activo = 0, fecha_eliminacion = CURRENT_TIMESTAMP WHERE id = ?
                """, (carga_id,))
                
                descripcion = f"Eliminó carga: {carga[0]} - {carga[1]} (RUT: {carga[2]})"
                cursor.execute("""
                    INSERT INTO notificaciones_admin (tipo, rut_trabajador, nombre_trabajador, descripcion)
                    VALUES ('ELIMINACION_CARGA', ?, ?, ?)
                """, (rut_trabajador, nombre_trabajador, descripcion))
                
                conn.commit()
                logger.info(f"Carga {carga_id} eliminada por {nombre_trabajador}")
                return True
        except Exception as e:
            logger.error(f"Error al eliminar carga: {e}")
            return False
    
    def dar_baja_seguro(self, registro_id: int, rut_trabajador: str, 
                        nombre_trabajador: str, motivo: str = "Solicitud del trabajador") -> bool:
        """Da de baja el seguro de un trabajador."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE registros_trabajador 
                    SET activo = 0, fecha_baja = CURRENT_TIMESTAMP, motivo_baja = ?
                    WHERE id = ?
                """, (motivo, registro_id))
                
                cursor.execute("""
                    UPDATE cargas SET activo = 0, fecha_eliminacion = CURRENT_TIMESTAMP
                    WHERE registro_id = ?
                """, (registro_id,))
                
                cursor.execute("""
                    INSERT INTO notificaciones_admin (tipo, rut_trabajador, nombre_trabajador, descripcion)
                    VALUES ('BAJA_SEGURO', ?, ?, ?)
                """, (rut_trabajador, nombre_trabajador, f"Solicitó BAJA del seguro. Motivo: {motivo}"))
                
                conn.commit()
                logger.info(f"Baja de seguro procesada para {nombre_trabajador}")
                return True
        except Exception as e:
            logger.error(f"Error al dar de baja: {e}")
            return False
    
    def obtener_notificaciones_pendientes(self) -> List[Dict]:
        """Obtiene las notificaciones pendientes."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM notificaciones_admin WHERE leida = 0 ORDER BY fecha DESC
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
                cursor.execute("UPDATE notificaciones_admin SET leida = 1 WHERE id = ?", (notificacion_id,))
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
    
    # ==================== CONTROL DE ENVÍO A ASEGURADORA ====================
    
    def obtener_registros_pendientes_envio(self) -> List[Dict]:
        """Obtiene registros que aún no han sido enviados a la aseguradora."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM registros_trabajador 
                    WHERE activo = 1 AND (enviado_aseguradora = 0 OR enviado_aseguradora IS NULL)
                    ORDER BY fecha_registro
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener registros pendientes: {e}")
            return []
    
    def exportar_y_marcar_enviado(self, archivo_salida: str, numero_lote: str) -> bool:
        """Exporta solo registros pendientes y los marca como enviados."""
        try:
            pendientes = self.obtener_registros_pendientes_envio()
            
            if not pendientes:
                return False
            
            Path(archivo_salida).parent.mkdir(parents=True, exist_ok=True)
            
            ids_pendientes = [p['id'] for p in pendientes]
            
            with sqlite3.connect(self.db_path) as conn:
                # Obtener datos para exportar
                placeholders = ','.join('?' * len(ids_pendientes))
                
                df_registros = pd.read_sql_query(f"""
                    SELECT 
                        rut_trabajador as 'RUT',
                        nombre_trabajador as 'Nombre',
                        email as 'Email',
                        banco as 'Banco',
                        tipo_cuenta as 'Tipo Cuenta',
                        numero_cuenta as 'Número Cuenta',
                        fecha_registro as 'Fecha Registro'
                    FROM registros_trabajador
                    WHERE id IN ({placeholders}) AND activo = 1
                    ORDER BY fecha_registro
                """, conn, params=ids_pendientes)
                
                df_cargas = pd.read_sql_query(f"""
                    SELECT 
                        r.rut_trabajador as 'RUT Trabajador',
                        r.nombre_trabajador as 'Nombre Trabajador',
                        c.tipo as 'Tipo Carga',
                        c.rut as 'RUT Carga',
                        c.nombre as 'Nombre Carga',
                        c.fecha_nacimiento as 'Fecha Nacimiento',
                        c.edad as 'Edad'
                    FROM cargas c
                    JOIN registros_trabajador r ON c.registro_id = r.id
                    WHERE r.id IN ({placeholders}) AND c.activo = 1 AND r.activo = 1
                    ORDER BY r.nombre_trabajador, c.tipo
                """, conn, params=ids_pendientes)
                
                # Formatear fechas
                if 'Fecha Registro' in df_registros.columns:
                    df_registros['Fecha Registro'] = pd.to_datetime(df_registros['Fecha Registro']).dt.strftime('%d-%m-%y')
                
                if 'Fecha Nacimiento' in df_cargas.columns:
                    df_cargas['Fecha Nacimiento'] = pd.to_datetime(df_cargas['Fecha Nacimiento']).dt.strftime('%d-%m-%y')
                
                # Escribir Excel
                with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
                    df_registros.to_excel(writer, sheet_name='Trabajadores', index=False)
                    df_cargas.to_excel(writer, sheet_name='Cargas Familiares', index=False)
                
                # Marcar como enviados
                cursor = conn.cursor()
                for reg_id in ids_pendientes:
                    cursor.execute("""
                        UPDATE registros_trabajador 
                        SET enviado_aseguradora = 1, 
                            fecha_envio_aseguradora = CURRENT_TIMESTAMP,
                            numero_lote = ?
                        WHERE id = ?
                    """, (numero_lote, reg_id))
                
                conn.commit()
            
            logger.info(f"Exportados {len(pendientes)} registros en lote {numero_lote}")
            return True
            
        except Exception as e:
            logger.error(f"Error al exportar y marcar enviado: {e}")
            return False
    
    def solo_exportar_pendientes(self, archivo_salida: str) -> bool:
        """Exporta registros pendientes SIN marcarlos como enviados (solo descarga)."""
        try:
            pendientes = self.obtener_registros_pendientes_envio()
            
            if not pendientes:
                return False
            
            Path(archivo_salida).parent.mkdir(parents=True, exist_ok=True)
            
            ids_pendientes = [p['id'] for p in pendientes]
            
            with sqlite3.connect(self.db_path) as conn:
                placeholders = ','.join('?' * len(ids_pendientes))
                
                df_registros = pd.read_sql_query(f"""
                    SELECT 
                        rut_trabajador as 'RUT',
                        nombre_trabajador as 'Nombre',
                        email as 'Email',
                        banco as 'Banco',
                        tipo_cuenta as 'Tipo Cuenta',
                        numero_cuenta as 'Número Cuenta',
                        fecha_registro as 'Fecha Registro'
                    FROM registros_trabajador
                    WHERE id IN ({placeholders}) AND activo = 1
                    ORDER BY fecha_registro
                """, conn, params=ids_pendientes)
                
                df_cargas = pd.read_sql_query(f"""
                    SELECT 
                        r.rut_trabajador as 'RUT Trabajador',
                        r.nombre_trabajador as 'Nombre Trabajador',
                        c.tipo as 'Tipo Carga',
                        c.rut as 'RUT Carga',
                        c.nombre as 'Nombre Carga',
                        c.fecha_nacimiento as 'Fecha Nacimiento',
                        c.edad as 'Edad'
                    FROM cargas c
                    JOIN registros_trabajador r ON c.registro_id = r.id
                    WHERE r.id IN ({placeholders}) AND c.activo = 1 AND r.activo = 1
                    ORDER BY r.nombre_trabajador, c.tipo
                """, conn, params=ids_pendientes)
                
                if 'Fecha Registro' in df_registros.columns:
                    df_registros['Fecha Registro'] = pd.to_datetime(df_registros['Fecha Registro']).dt.strftime('%d-%m-%y')
                
                if 'Fecha Nacimiento' in df_cargas.columns:
                    df_cargas['Fecha Nacimiento'] = pd.to_datetime(df_cargas['Fecha Nacimiento']).dt.strftime('%d-%m-%y')
                
                with pd.ExcelWriter(archivo_salida, engine='openpyxl') as writer:
                    df_registros.to_excel(writer, sheet_name='Trabajadores', index=False)
                    df_cargas.to_excel(writer, sheet_name='Cargas Familiares', index=False)
            
            logger.info(f"Exportados {len(pendientes)} registros (sin marcar)")
            return True
            
        except Exception as e:
            logger.error(f"Error al exportar: {e}")
            return False
    
    def marcar_registros_enviados(self, numero_lote: str) -> bool:
        """Marca los registros pendientes como enviados (después de enviar email)."""
        try:
            pendientes = self.obtener_registros_pendientes_envio()
            
            if not pendientes:
                return False
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                for reg in pendientes:
                    # Marcar registro como enviado
                    cursor.execute("""
                        UPDATE registros_trabajador 
                        SET enviado_aseguradora = 1, 
                            fecha_envio_aseguradora = CURRENT_TIMESTAMP,
                            numero_lote = ?
                        WHERE id = ?
                    """, (numero_lote, reg['id']))
                    
                    # También marcar las cargas de este registro
                    cursor.execute("""
                        UPDATE cargas 
                        SET enviado_aseguradora = 1, 
                            fecha_envio_aseguradora = CURRENT_TIMESTAMP,
                            numero_lote = ?
                        WHERE registro_id = ? AND activo = 1
                    """, (numero_lote, reg['id']))
                
                # Marcar cargas nuevas de registros ya enviados
                cursor.execute("""
                    UPDATE cargas 
                    SET enviado_aseguradora = 1, 
                        fecha_envio_aseguradora = CURRENT_TIMESTAMP,
                        numero_lote = ?
                    WHERE activo = 1 AND (enviado_aseguradora = 0 OR enviado_aseguradora IS NULL)
                """, (numero_lote,))
                
                conn.commit()
            
            logger.info(f"Marcados {len(pendientes)} registros como enviados (lote {numero_lote})")
            return True
            
        except Exception as e:
            logger.error(f"Error al marcar como enviados: {e}")
            return False
    
    def obtener_cargas_nuevas_pendientes(self) -> List[Dict]:
        """Obtiene cargas nuevas de trabajadores ya enviados que aún no se han reportado."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT c.*, r.nombre_trabajador, r.rut_trabajador
                    FROM cargas c
                    JOIN registros_trabajador r ON c.registro_id = r.id
                    WHERE r.enviado_aseguradora = 1 
                    AND c.activo = 1 
                    AND (c.enviado_aseguradora = 0 OR c.enviado_aseguradora IS NULL)
                """)
                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error al obtener cargas pendientes: {e}")
            return []
    
    def reiniciar_estado_envio(self):
        """Reinicia el estado de envío de todos los registros y cargas (para pruebas)."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Reiniciar registros
                cursor.execute("""
                    UPDATE registros_trabajador 
                    SET enviado_aseguradora = 0, 
                        fecha_envio_aseguradora = NULL,
                        numero_lote = NULL
                    WHERE activo = 1
                """)
                filas_registros = cursor.rowcount
                
                # Reiniciar cargas
                cursor.execute("""
                    UPDATE cargas 
                    SET enviado_aseguradora = 0, 
                        fecha_envio_aseguradora = NULL,
                        numero_lote = NULL
                    WHERE activo = 1
                """)
                filas_cargas = cursor.rowcount
                conn.commit()
            
            total = filas_registros + filas_cargas
            logger.info(f"Estado de envío reiniciado: {filas_registros} registros, {filas_cargas} cargas")
            return filas_registros  # Devuelve cantidad de registros actualizados
            
        except Exception as e:
            logger.error(f"Error al reiniciar estado: {e}")
            return -1  # -1 indica error

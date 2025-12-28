"""
Sistema de Registro de Seguro Complementario - Versión 2.0
Con validación de empleados, datos bancarios y correo automático
"""
import streamlit as st
import datetime
from pathlib import Path
import os

# Importar módulos propios
from config import APP_TITLE, MAX_HIJOS, EDAD_MAXIMA_HIJO
from utils import (
    validar_rut, 
    formatear_rut, 
    validar_nombre, 
    validar_fecha_nacimiento,
    calcular_edad,
    validar_email,
    validar_numero_cuenta,
    logger
)
from services import (
    DatabaseService,
    BANCOS_CHILE,
    TIPOS_CUENTA,
    enviar_correo_confirmacion,
    simular_envio_correo
)


# Configuración de la página
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicializar servicio de base de datos
@st.cache_resource
def get_database():
    """Obtiene instancia del servicio de base de datos."""
    return DatabaseService()

db = get_database()


def formato_fecha_chile(fecha) -> str:
    """Convierte fecha a formato chileno DD-MM-YY."""
    if isinstance(fecha, str):
        try:
            fecha = datetime.datetime.strptime(fecha, "%Y-%m-%d").date()
        except:
            return fecha
    return fecha.strftime("%d-%m-%y")


# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .success-box {
        padding: 1rem;
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .error-box {
        padding: 1rem;
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        background-color: #d1ecf1;
        border-left: 5px solid #17a2b8;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        border-radius: 5px;
        margin: 1rem 0;
    }
    .stButton>button {
        width: 100%;
    }
    .card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


# ==================== INICIALIZACIÓN DE SESSION STATE ====================

def init_session_state():
    """Inicializa el estado de la sesión."""
    if 'trabajador_validado' not in st.session_state:
        st.session_state.trabajador_validado = False
    if 'datos_trabajador' not in st.session_state:
        st.session_state.datos_trabajador = None
    if 'cargas_temporales' not in st.session_state:
        st.session_state.cargas_temporales = []
    if 'registro_completado' not in st.session_state:
        st.session_state.registro_completado = False
    if 'registro_id' not in st.session_state:
        st.session_state.registro_id = None
    if 'modo_admin' not in st.session_state:
        st.session_state.modo_admin = False
    if 'registro_existente' not in st.session_state:
        st.session_state.registro_existente = None


def reset_formulario():
    """Reinicia el formulario."""
    st.session_state.trabajador_validado = False
    st.session_state.datos_trabajador = None
    st.session_state.cargas_temporales = []
    st.session_state.registro_completado = False
    st.session_state.registro_id = None
    st.session_state.registro_existente = None


# ==================== BARRA LATERAL ====================

# Contraseña de administrador (cambiar en producción)
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin2024')

def sidebar_menu():
    """Menú de la barra lateral."""
    st.sidebar.header("🏢 Seguro Complementario")
    
    # Verificar si el admin está autenticado
    if 'admin_autenticado' not in st.session_state:
        st.session_state.admin_autenticado = False
    
    # Mostrar vista según estado
    if st.session_state.admin_autenticado:
        st.sidebar.success("🔐 Modo Administrador")
        
        if st.sidebar.button("🚪 Cerrar Sesión Admin"):
            st.session_state.admin_autenticado = False
            st.session_state.modo_admin = False
            st.rerun()
        
        st.session_state.modo_admin = True
        
        st.sidebar.markdown("---")
        
        # Estadísticas para admin
        st.sidebar.header("📊 Estadísticas")
        stats = db.obtener_estadisticas()
        
        col1, col2 = st.sidebar.columns(2)
        col1.metric("Empleados", stats.get('total_empleados', 0))
        col2.metric("Registros", stats.get('total_registros', 0))
        
        st.sidebar.metric("Total Cargas", stats.get('total_cargas', 0))
        st.sidebar.metric("Emails Enviados", stats.get('emails_enviados', 0))
        
        if stats.get('cargas_por_tipo'):
            st.sidebar.subheader("Por Tipo")
            for tipo, cantidad in stats['cargas_por_tipo'].items():
                st.sidebar.write(f"**{tipo}:** {cantidad}")
    else:
        st.session_state.modo_admin = False
        
        st.sidebar.markdown("---")
        st.sidebar.caption("👤 Modo Trabajador")
        
        # Botón para acceder como admin
        with st.sidebar.expander("🔐 Acceso Administrador"):
            password = st.text_input("Contraseña:", type="password", key="admin_pwd")
            if st.button("Ingresar"):
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_autenticado = True
                    st.session_state.modo_admin = True
                    st.rerun()
                else:
                    st.error("❌ Contraseña incorrecta")


# ==================== VISTA TRABAJADOR ====================

def paso1_validar_trabajador():
    """Paso 1: Validar RUT del trabajador contra base de datos de empleados."""
    st.subheader("📋 Paso 1: Validación de Trabajador")
    
    st.info("👋 Bienvenido/a. Por favor ingrese su RUT para verificar que es empleado de la empresa.")
    
    with st.form("form_validar_rut"):
        rut_input = st.text_input(
            "Ingrese su RUT",
            placeholder="12.345.678-9",
            help="Ingrese su RUT con o sin puntos y guión"
        )
        
        validar_btn = st.form_submit_button("🔍 Validar RUT", type="primary")
        
        if validar_btn:
            if not rut_input:
                st.error("❌ Por favor ingrese su RUT")
                return
            
            # Validar formato de RUT
            rut_valido, mensaje = validar_rut(rut_input)
            if not rut_valido:
                st.error(f"❌ {mensaje}")
                return
            
            # Formatear RUT
            rut_formateado = formatear_rut(rut_input)
            
            # Verificar si es empleado de la empresa
            es_empleado, datos_empleado = db.verificar_empleado_existe(rut_formateado)
            
            if not es_empleado:
                st.error("""
                ❌ **RUT no encontrado en la base de datos de empleados.**
                
                Si usted es empleado de la empresa y su RUT no está registrado, 
                por favor contacte al departamento de Recursos Humanos.
                """)
                logger.warning(f"Intento de acceso con RUT no registrado: {rut_formateado}")
                return
            
            # Verificar si ya tiene un registro activo en el seguro
            registro_existente = db.obtener_registro_por_rut(rut_formateado)
            
            if registro_existente:
                # Redirigir a portal de autoservicio
                st.session_state.trabajador_validado = True
                st.session_state.registro_existente = registro_existente
                st.session_state.datos_trabajador = {
                    'rut': rut_formateado,
                    'nombre': datos_empleado['nombre'],
                    'email_registrado': datos_empleado.get('email', ''),
                    'tiene_registro': True
                }
                st.success(f"✅ Bienvenido/a de nuevo, **{datos_empleado['nombre']}**")
                st.rerun()
            else:
                # Nuevo registro
                st.session_state.trabajador_validado = True
                st.session_state.registro_existente = None
                st.session_state.datos_trabajador = {
                    'rut': rut_formateado,
                    'nombre': datos_empleado['nombre'],
                    'email_registrado': datos_empleado.get('email', ''),
                    'tiene_registro': False
                }
                st.success(f"✅ Bienvenido/a, **{datos_empleado['nombre']}**")
                st.rerun()


def paso2_datos_contacto_bancarios():
    """Paso 2: Completar datos de contacto y bancarios."""
    st.subheader("📧 Paso 2: Datos de Contacto y Bancarios")
    
    datos = st.session_state.datos_trabajador
    
    st.write(f"**Trabajador:** {datos['nombre']}")
    st.write(f"**RUT:** {datos['rut']}")
    
    st.markdown("---")
    
    with st.form("form_contacto"):
        st.markdown("### 📧 Correo Electrónico")
        email = st.text_input(
            "Correo electrónico",
            value=datos.get('email_registrado', ''),
            placeholder="su.correo@ejemplo.com",
            help="Ingrese un correo válido. Recibirá la confirmación aquí."
        )
        
        st.markdown("### 🏦 Datos Bancarios (opcional)")
        st.caption("Complete estos datos si desea que los reembolsos se depositen en su cuenta.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            banco = st.selectbox(
                "Banco",
                options=[""] + BANCOS_CHILE,
                index=0,
                help="Seleccione su banco"
            )
            
            tipo_cuenta = st.selectbox(
                "Tipo de Cuenta",
                options=[""] + TIPOS_CUENTA,
                index=0,
                help="Seleccione el tipo de cuenta"
            )
        
        with col2:
            numero_cuenta = st.text_input(
                "Número de Cuenta",
                placeholder="Ej: 12345678901",
                help="Ingrese el número de cuenta sin puntos ni guiones"
            )
        
        guardar_btn = st.form_submit_button("💾 Guardar y Continuar", type="primary")
        
        if guardar_btn:
            # Validar email
            email_valido, msg_email = validar_email(email)
            if not email_valido:
                st.error(f"❌ {msg_email}")
                return
            
            # Validar número de cuenta si se ingresó
            if numero_cuenta:
                cuenta_valida, msg_cuenta = validar_numero_cuenta(numero_cuenta)
                if not cuenta_valida:
                    st.error(f"❌ {msg_cuenta}")
                    return
            
            # Actualizar datos
            st.session_state.datos_trabajador.update({
                'email': email.lower().strip(),
                'banco': banco if banco else None,
                'tipo_cuenta': tipo_cuenta if tipo_cuenta else None,
                'numero_cuenta': numero_cuenta if numero_cuenta else None,
                'paso_completado': 2
            })
            
            st.success("✅ Datos guardados correctamente")
            st.rerun()


def paso3_agregar_cargas():
    """Paso 3: Agregar cargas familiares."""
    st.subheader("👨‍👩‍👧‍👦 Paso 3: Registro de Cargas Familiares")
    
    datos = st.session_state.datos_trabajador
    
    # Mostrar resumen
    with st.expander("📋 Ver datos del trabajador", expanded=False):
        st.write(f"**Nombre:** {datos['nombre']}")
        st.write(f"**RUT:** {datos['rut']}")
        st.write(f"**Email:** {datos['email']}")
        if datos.get('banco'):
            st.write(f"**Banco:** {datos['banco']} - {datos.get('tipo_cuenta', '')}")
            st.write(f"**Cuenta:** {datos.get('numero_cuenta', '')}")
    
    st.markdown("---")
    
    # Mostrar cargas agregadas
    if st.session_state.cargas_temporales:
        st.markdown("### ✅ Cargas Agregadas")
        for i, carga in enumerate(st.session_state.cargas_temporales):
            col1, col2, col3, col4, col5, col6 = st.columns([1.5, 2.5, 2, 1.5, 1, 0.5])
            with col1:
                st.write(f"**{carga['tipo']}**")
            with col2:
                st.write(carga['nombre'])
            with col3:
                st.write(carga['rut'])
            with col4:
                st.write(f"Nac: {formato_fecha_chile(carga['fecha_nacimiento'])}")
            with col5:
                st.write(f"{carga['edad']} años")
            with col6:
                if st.button("❌", key=f"del_{i}"):
                    st.session_state.cargas_temporales.pop(i)
                    st.rerun()
        st.markdown("---")
    
    # Formulario para agregar carga
    st.markdown("### ➕ Agregar Nueva Carga")
    
    tipo_carga = st.radio(
        "Tipo de carga",
        ["Cónyuge", "Hijo/a"],
        horizontal=True
    )
    
    with st.form("form_carga"):
        col1, col2 = st.columns(2)
        
        with col1:
            rut_carga = st.text_input(
                "RUT",
                placeholder="12.345.678-9"
            )
            nombre_carga = st.text_input(
                "Nombre completo",
                placeholder="Nombre Apellido"
            )
        
        with col2:
            fecha_nac = st.date_input(
                "Fecha de nacimiento (DD/MM/AAAA)",
                max_value=datetime.date.today(),
                min_value=datetime.date(1900, 1, 1),
                format="DD/MM/YYYY"
            )
        
        agregar_btn = st.form_submit_button("➕ Agregar Carga")
        
        if agregar_btn:
            # Validaciones
            rut_valido, msg_rut = validar_rut(rut_carga)
            if not rut_valido:
                st.error(f"❌ {msg_rut}")
                return
            
            nombre_valido, msg_nombre = validar_nombre(nombre_carga)
            if not nombre_valido:
                st.error(f"❌ {msg_nombre}")
                return
            
            # Validar edad para hijos
            edad_maxima = EDAD_MAXIMA_HIJO if tipo_carga == "Hijo/a" else None
            fecha_valida, msg_fecha = validar_fecha_nacimiento(fecha_nac, edad_maxima)
            if not fecha_valida:
                st.error(f"❌ {msg_fecha}")
                return
            
            rut_formateado = formatear_rut(rut_carga)
            
            # Verificar duplicado
            for carga in st.session_state.cargas_temporales:
                if carga['rut'] == rut_formateado:
                    st.error("❌ Este RUT ya fue agregado")
                    return
            
            # Agregar carga temporal
            st.session_state.cargas_temporales.append({
                'tipo': tipo_carga.replace('/a', ''),
                'rut': rut_formateado,
                'nombre': nombre_carga.title(),
                'fecha_nacimiento': fecha_nac,
                'edad': calcular_edad(fecha_nac)
            })
            
            st.success(f"✅ {tipo_carga} agregado/a correctamente")
            st.rerun()
    
    st.markdown("---")
    
    # Botones de navegación
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Volver", use_container_width=True):
            st.session_state.datos_trabajador['paso_completado'] = 1
            st.rerun()
    
    with col2:
        if st.button("✅ Finalizar Registro", type="primary", use_container_width=True):
            if not st.session_state.cargas_temporales:
                st.warning("⚠️ No ha agregado ninguna carga. ¿Desea continuar sin cargas?")
            
            st.session_state.datos_trabajador['paso_completado'] = 3
            st.rerun()


def paso4_confirmar_enviar():
    """Paso 4: Confirmar y enviar registro."""
    st.subheader("📤 Paso 4: Confirmación y Envío")
    
    datos = st.session_state.datos_trabajador
    cargas = st.session_state.cargas_temporales
    
    st.markdown("### 📋 Resumen de su Registro")
    
    # Datos del trabajador
    st.markdown("#### 👤 Datos del Trabajador")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nombre:** {datos['nombre']}")
        st.write(f"**RUT:** {datos['rut']}")
        st.write(f"**Email:** {datos['email']}")
    with col2:
        if datos.get('banco'):
            st.write(f"**Banco:** {datos['banco']}")
            st.write(f"**Tipo Cuenta:** {datos.get('tipo_cuenta', 'N/A')}")
            st.write(f"**Número:** {datos.get('numero_cuenta', 'N/A')}")
    
    # Cargas familiares
    st.markdown("---")
    st.markdown("#### 👨‍👩‍👧‍👦 Cargas Familiares")
    
    if cargas:
        for carga in cargas:
            fecha_nac = formato_fecha_chile(carga['fecha_nacimiento'])
            st.write(f"- **{carga['tipo']}:** {carga['nombre']} (RUT: {carga['rut']}, Nac: {fecha_nac}, {carga['edad']} años)")
    else:
        st.write("*No se registraron cargas familiares*")
    
    st.markdown("---")
    
    # Términos y condiciones
    aceptar_terminos = st.checkbox(
        "✅ Declaro que los datos ingresados son correctos y acepto las condiciones del seguro complementario."
    )
    
    st.markdown("---")
    
    # Botones
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Volver a Editar", use_container_width=True):
            st.session_state.datos_trabajador['paso_completado'] = 2
            st.rerun()
    
    with col2:
        enviar_btn = st.button(
            "📤 Enviar Registro",
            type="primary",
            disabled=not aceptar_terminos,
            use_container_width=True
        )
        
        if enviar_btn:
            with st.spinner("Procesando registro..."):
                # Crear registro en base de datos
                registro_id = db.crear_registro_trabajador(
                    rut_trabajador=datos['rut'],
                    nombre_trabajador=datos['nombre'],
                    email=datos['email'],
                    banco=datos.get('banco'),
                    tipo_cuenta=datos.get('tipo_cuenta'),
                    numero_cuenta=datos.get('numero_cuenta')
                )
                
                if not registro_id:
                    st.error("❌ Error al crear el registro. Por favor intente nuevamente.")
                    return
                
                # Agregar cargas
                for carga in cargas:
                    db.agregar_carga_a_registro(
                        registro_id=registro_id,
                        tipo=carga['tipo'],
                        rut=carga['rut'],
                        nombre=carga['nombre'],
                        fecha_nacimiento=carga['fecha_nacimiento'],
                        edad=carga['edad']
                    )
                
                # Obtener registro completo para el email
                registro_completo = db.obtener_registro_con_cargas(registro_id)
                
                # Intentar enviar correo
                smtp_configurado = os.getenv('SMTP_USER') and os.getenv('SMTP_PASSWORD')
                
                if smtp_configurado:
                    exito_email, msg_email = enviar_correo_confirmacion(registro_completo)
                else:
                    exito_email, msg_email = simular_envio_correo(registro_completo)
                
                if exito_email:
                    db.marcar_email_enviado(registro_id)
                
                # Marcar como completado
                st.session_state.registro_completado = True
                st.session_state.registro_id = registro_id
                logger.info(f"Registro completado: ID {registro_id} para {datos['nombre']}")
                st.rerun()


def mostrar_confirmacion_final():
    """Muestra pantalla de confirmación final."""
    st.balloons()
    
    st.markdown("""
    <div style="text-align: center; padding: 40px;">
        <h1 style="color: #28a745;">✅ ¡Registro Exitoso!</h1>
    </div>
    """, unsafe_allow_html=True)
    
    datos = st.session_state.datos_trabajador
    
    st.success(f"""
    **Estimado/a {datos['nombre']}**
    
    Su registro ha sido procesado correctamente.
    
    📧 **Se ha enviado un correo de confirmación a:** {datos['email']}
    
    📅 **Fecha estimada de alta:** Sus cargas estarán habilitadas en aproximadamente **15 días hábiles**.
    """)
    
    st.info("""
    **Próximos pasos:**
    1. Revise su correo electrónico para ver el comprobante
    2. Guarde el correo como respaldo
    3. Si detecta algún error, contacte a Recursos Humanos
    """)
    
    if st.button("🔄 Realizar otro registro", type="primary"):
        reset_formulario()
        st.rerun()


def portal_autoservicio():
    """Portal de autoservicio para trabajadores con registro existente."""
    datos = st.session_state.datos_trabajador
    registro = st.session_state.registro_existente
    
    st.markdown("### 👤 Mi Registro de Seguro")
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nombre:** {datos['nombre']}")
        st.write(f"**RUT:** {datos['rut']}")
        st.write(f"**Email:** {registro['email']}")
    with col2:
        if registro.get('banco'):
            st.write(f"**Banco:** {registro['banco']}")
            st.write(f"**Tipo Cuenta:** {registro.get('tipo_cuenta', 'N/A')}")
    
    st.markdown("---")
    
    # Tabs de autoservicio
    tab1, tab2, tab3, tab4 = st.tabs(["👁️ Mis Cargas", "➕ Agregar Carga", "❌ Eliminar Carga", "🚫 Baja del Seguro"])
    
    with tab1:
        st.subheader("👨‍👩‍👧‍👦 Mis Cargas Familiares")
        cargas = registro.get('cargas', [])
        
        if cargas:
            for carga in cargas:
                fecha_nac = formato_fecha_chile(carga['fecha_nacimiento'])
                st.write(f"• **{carga['tipo']}:** {carga['nombre']} (RUT: {carga['rut']}, Nac: {fecha_nac}, {carga['edad']} años)")
        else:
            st.info("No tiene cargas familiares registradas.")
    
    with tab2:
        st.subheader("➕ Agregar Nueva Carga")
        
        tipo_carga = st.radio(
            "Tipo de carga",
            ["Cónyuge", "Hijo/a"],
            horizontal=True,
            key="tipo_nueva_carga"
        )
        
        with st.form("form_nueva_carga"):
            col1, col2 = st.columns(2)
            
            with col1:
                rut_carga = st.text_input("RUT", placeholder="12.345.678-9", key="rut_nueva_carga")
                nombre_carga = st.text_input("Nombre completo", placeholder="Nombre Apellido", key="nombre_nueva_carga")
            
            with col2:
                fecha_nac = st.date_input(
                    "Fecha de nacimiento (DD/MM/AAAA)",
                    max_value=datetime.date.today(),
                    min_value=datetime.date(1900, 1, 1),
                    format="DD/MM/YYYY",
                    key="fecha_nueva_carga"
                )
            
            if st.form_submit_button("➕ Agregar Carga", type="primary"):
                # Validaciones
                rut_valido, msg_rut = validar_rut(rut_carga)
                if not rut_valido:
                    st.error(f"❌ {msg_rut}")
                else:
                    nombre_valido, msg_nombre = validar_nombre(nombre_carga)
                    if not nombre_valido:
                        st.error(f"❌ {msg_nombre}")
                    else:
                        edad_maxima = EDAD_MAXIMA_HIJO if tipo_carga == "Hijo/a" else None
                        fecha_valida, msg_fecha = validar_fecha_nacimiento(fecha_nac, edad_maxima)
                        if not fecha_valida:
                            st.error(f"❌ {msg_fecha}")
                        else:
                            rut_formateado = formatear_rut(rut_carga)
                            edad = calcular_edad(fecha_nac)
                            
                            if db.agregar_carga_a_registro(
                                registro_id=registro['id'],
                                tipo=tipo_carga.replace('/a', ''),
                                rut=rut_formateado,
                                nombre=nombre_carga.title(),
                                fecha_nacimiento=fecha_nac,
                                edad=edad
                            ):
                                st.success(f"✅ {tipo_carga} agregado/a correctamente")
                                # Refrescar registro
                                st.session_state.registro_existente = db.obtener_registro_por_rut(datos['rut'])
                                st.rerun()
                            else:
                                st.error("❌ Error al agregar la carga")
    
    with tab3:
        st.subheader("❌ Eliminar Carga")
        cargas = registro.get('cargas', [])
        
        if cargas:
            st.warning("⚠️ Al eliminar una carga, se notificará automáticamente al administrador para informar al seguro.")
            
            for carga in cargas:
                col1, col2, col3 = st.columns([4, 2, 1])
                with col1:
                    fecha_nac = formato_fecha_chile(carga['fecha_nacimiento'])
                    st.write(f"**{carga['tipo']}:** {carga['nombre']} (RUT: {carga['rut']})")
                with col2:
                    st.write(f"Nac: {fecha_nac}")
                with col3:
                    if st.button("🗑️ Eliminar", key=f"del_carga_{carga['id']}"):
                        if db.eliminar_carga(carga['id'], datos['rut'], datos['nombre']):
                            st.success(f"✅ Carga eliminada. Se notificó al administrador.")
                            st.session_state.registro_existente = db.obtener_registro_por_rut(datos['rut'])
                            st.rerun()
                        else:
                            st.error("❌ Error al eliminar la carga")
        else:
            st.info("No tiene cargas para eliminar.")
    
    with tab4:
        st.subheader("🚫 Solicitar Baja del Seguro")
        
        st.error("""
        ⚠️ **ATENCIÓN:** Esta acción dará de baja su inscripción al seguro complementario.
        
        - Todas sus cargas familiares serán eliminadas del seguro
        - Esta acción es **INMEDIATA**
        - Se notificará al administrador para informar al seguro
        """)
        
        motivo = st.text_area(
            "Motivo de la baja (opcional)",
            placeholder="Ej: Cambio de empresa, ya no deseo el beneficio, etc.",
            key="motivo_baja"
        )
        
        confirmar = st.checkbox("✅ Confirmo que deseo dar de baja mi seguro complementario")
        
        if st.button("🚫 Confirmar Baja del Seguro", type="primary", disabled=not confirmar):
            if db.dar_baja_seguro(
                registro_id=registro['id'],
                rut_trabajador=datos['rut'],
                nombre_trabajador=datos['nombre'],
                motivo=motivo or "Solicitud del trabajador"
            ):
                st.success("✅ Su baja ha sido procesada correctamente.")
                st.info("Se ha notificado al administrador. Recibirá confirmación por correo.")
                st.session_state.registro_existente = None
                st.session_state.datos_trabajador['tiene_registro'] = False
                
                if st.button("🔄 Volver al inicio"):
                    reset_formulario()
                    st.rerun()
            else:
                st.error("❌ Error al procesar la baja")
    
    st.markdown("---")
    
    if st.button("🚪 Cerrar Sesión"):
        reset_formulario()
        st.rerun()


def vista_trabajador():
    """Vista principal para el trabajador."""
    st.markdown('<div class="main-header">📋 Registro de Seguro Complementario</div>', unsafe_allow_html=True)
    
    if st.session_state.registro_completado:
        mostrar_confirmacion_final()
        return
    
    # Si ya tiene registro, mostrar portal de autoservicio
    if st.session_state.trabajador_validado and st.session_state.datos_trabajador.get('tiene_registro'):
        st.markdown('<p class="sub-header">Gestione sus cargas familiares</p>', unsafe_allow_html=True)
        portal_autoservicio()
        return
    
    # Nuevo registro - flujo normal
    st.markdown('<p class="sub-header">Complete el formulario para inscribir a sus cargas familiares</p>', unsafe_allow_html=True)
    
    # Progreso
    paso_actual = 1
    if st.session_state.trabajador_validado:
        paso_actual = st.session_state.datos_trabajador.get('paso_completado', 1) + 1
    
    st.progress(paso_actual / 4)
    st.caption(f"Paso {paso_actual} de 4")
    
    # Mostrar paso correspondiente
    if not st.session_state.trabajador_validado:
        paso1_validar_trabajador()
    elif st.session_state.datos_trabajador.get('paso_completado', 0) < 2:
        paso2_datos_contacto_bancarios()
    elif st.session_state.datos_trabajador.get('paso_completado', 0) < 3:
        paso3_agregar_cargas()
    else:
        paso4_confirmar_enviar()


# ==================== VISTA ADMINISTRADOR ====================

def vista_administrador():
    """Vista para el administrador (empleador)."""
    st.markdown('<div class="main-header">🔐 Panel de Administración</div>', unsafe_allow_html=True)
    
    # Mostrar badge de notificaciones pendientes
    notificaciones = db.obtener_notificaciones_pendientes()
    if notificaciones:
        st.warning(f"🔔 Tiene **{len(notificaciones)}** notificación(es) pendiente(s)")
    
    # Tabs de administración
    tab1, tab2, tab3, tab4 = st.tabs(["🔔 Notificaciones", "📊 Registros", "👥 Empleados", "📥 Exportar"])
    
    with tab1:
        st.subheader("🔔 Notificaciones de Cambios")
        
        if notificaciones:
            if st.button("✅ Marcar todas como leídas"):
                db.marcar_todas_notificaciones_leidas()
                st.rerun()
            
            st.markdown("---")
            
            for notif in notificaciones:
                tipo_emoji = "❌" if notif['tipo'] == 'ELIMINACION_CARGA' else "🚫"
                tipo_texto = "Eliminación de Carga" if notif['tipo'] == 'ELIMINACION_CARGA' else "Baja de Seguro"
                
                with st.container():
                    col1, col2, col3 = st.columns([1, 4, 1])
                    with col1:
                        st.write(f"### {tipo_emoji}")
                    with col2:
                        st.write(f"**{tipo_texto}**")
                        st.write(f"**Trabajador:** {notif['nombre_trabajador']} ({notif['rut_trabajador']})")
                        st.write(f"**Detalle:** {notif['descripcion']}")
                        st.caption(f"📅 {notif['fecha']}")
                    with col3:
                        if st.button("✓", key=f"marcar_{notif['id']}"):
                            db.marcar_notificacion_leida(notif['id'])
                            st.rerun()
                    st.markdown("---")
        else:
            st.success("✅ No hay notificaciones pendientes")
    
    with tab2:
        st.subheader("📋 Registros de Trabajadores")
        
        registros = db.obtener_todos_registros()
        
        if registros:
            for reg in registros:
                with st.expander(f"👤 {reg['nombre_trabajador']} - {reg['rut_trabajador']}", expanded=False):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**Email:** {reg['email']}")
                        st.write(f"**Fecha Registro:** {reg['fecha_registro']}")
                        st.write(f"**Email Enviado:** {'✅' if reg['email_enviado'] else '❌'}")
                    with col2:
                        st.write(f"**Banco:** {reg.get('banco') or 'No especificado'}")
                        st.write(f"**Tipo Cuenta:** {reg.get('tipo_cuenta') or 'N/A'}")
                        st.write(f"**Número Cuenta:** {reg.get('numero_cuenta') or 'N/A'}")
                    
                    st.write(f"**Cargas:** {reg.get('nombres_cargas') or 'Sin cargas'}")
        else:
            st.info("No hay registros aún.")
    
    with tab3:
        st.subheader("👥 Gestión de Empleados")
        
        # Formulario para agregar empleado
        st.markdown("#### ➕ Agregar Empleado")
        
        with st.form("form_nuevo_empleado"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                nuevo_rut = st.text_input("RUT", placeholder="12.345.678-9")
            with col2:
                nuevo_nombre = st.text_input("Nombre Completo")
            with col3:
                nuevo_email = st.text_input("Email (opcional)")
            
            if st.form_submit_button("➕ Agregar Empleado"):
                if nuevo_rut and nuevo_nombre:
                    rut_valido, msg = validar_rut(nuevo_rut)
                    if rut_valido:
                        rut_fmt = formatear_rut(nuevo_rut)
                        if db.agregar_empleado(rut_fmt, nuevo_nombre.title(), nuevo_email):
                            st.success(f"✅ Empleado {nuevo_nombre} agregado")
                            st.rerun()
                        else:
                            st.error("❌ El empleado ya existe")
                    else:
                        st.error(f"❌ {msg}")
                else:
                    st.error("❌ Complete RUT y Nombre")
        
        st.markdown("---")
        
        # Lista de empleados
        st.markdown("#### 📋 Empleados Registrados")
        empleados = db.obtener_todos_empleados()
        
        if empleados:
            for emp in empleados:
                st.write(f"• **{emp['nombre']}** - RUT: {emp['rut']} - Email: {emp.get('email') or 'N/A'}")
        else:
            st.info("No hay empleados registrados. Agregue empleados para que puedan usar el sistema.")
        
        st.markdown("---")
        
        # Importar desde Excel
        st.markdown("#### 📤 Importar desde Excel")
        st.caption("El archivo debe tener columnas: RUT, Nombre, Email (opcional)")
        
        archivo = st.file_uploader("Seleccionar archivo Excel", type=['xlsx', 'xls'])
        
        if archivo:
            if st.button("📥 Importar Empleados"):
                # Guardar archivo temporal
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as f:
                    f.write(archivo.read())
                    temp_path = f.name
                
                exitosos, fallidos = db.importar_empleados_excel(temp_path)
                
                if exitosos > 0:
                    st.success(f"✅ {exitosos} empleados importados correctamente")
                if fallidos > 0:
                    st.warning(f"⚠️ {fallidos} registros fallidos (duplicados o datos inválidos)")
                
                os.unlink(temp_path)
                st.rerun()
    
    with tab4:
        st.subheader("📥 Exportar Datos para el Seguro")
        
        st.info("""
        Exporte todos los registros en formato Excel para enviar a la compañía de seguros.
        El archivo incluye dos hojas:
        - **Trabajadores:** Datos de contacto y bancarios
        - **Cargas Familiares:** Todas las cargas registradas
        """)
        
        if st.button("📊 Generar Reporte Excel", type="primary"):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = f"exports/registros_seguro_{timestamp}.xlsx"
            
            if db.exportar_registros_excel(archivo):
                st.success(f"✅ Archivo generado: `{archivo}`")
                
                with open(archivo, 'rb') as f:
                    st.download_button(
                        label="⬇️ Descargar Excel",
                        data=f,
                        file_name=f"registros_seguro_{timestamp}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.error("❌ Error al generar el archivo")


# ==================== MAIN ====================

def main():
    """Función principal de la aplicación."""
    init_session_state()
    sidebar_menu()
    
    if st.session_state.modo_admin:
        vista_administrador()
    else:
        vista_trabajador()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Error crítico: {str(e)}")
        logger.critical(f"Error crítico en aplicación: {e}", exc_info=True)

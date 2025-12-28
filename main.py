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
    simular_envio_correo,
    enviar_correo_aseguradora
)


# Configuración de la página
st.set_page_config(
    page_title=APP_TITLE,
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed"
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


# Estilos CSS corporativos
st.markdown("""
<style>
    /* Importar fuente profesional */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Variables de colores corporativos */
    :root {
        --primary-color: #1e3a5f;
        --secondary-color: #2e5984;
        --accent-color: #4a90d9;
        --success-color: #28a745;
        --warning-color: #ffc107;
        --danger-color: #dc3545;
        --text-dark: #333333;
        --text-light: #666666;
        --bg-light: #f8f9fa;
        --border-color: #e0e0e0;
    }
    
    /* Tipografía general */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header principal */
    .main-header {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
    }
    
    .sub-header {
        text-align: center;
        color: var(--text-light);
        font-size: 1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Header con logo */
    .corporate-header {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 1rem;
        padding: 1rem 0;
        margin-bottom: 1rem;
        border-bottom: 3px solid var(--primary-color);
    }
    
    .corporate-header img {
        height: 60px;
        width: auto;
    }
    
    .corporate-header h1 {
        margin: 0;
        color: var(--primary-color);
        font-size: 1.5rem;
        font-weight: 700;
    }
    
    /* Cajas de estado */
    .success-box {
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
        border-left: 4px solid var(--success-color);
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-box {
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
        border-left: 4px solid var(--danger-color);
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .info-box {
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #d1ecf1 0%, #bee5eb 100%);
        border-left: 4px solid var(--accent-color);
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .warning-box {
        padding: 1rem 1.5rem;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeeba 100%);
        border-left: 4px solid var(--warning-color);
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Botones más profesionales */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1rem;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Cards mejoradas */
    .card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid var(--border-color);
        margin: 1rem 0;
    }
    
    /* Sidebar más limpio */
    .css-1d391kg {
        background-color: var(--bg-light);
    }
    
    /* Footer corporativo */
    .corporate-footer {
        text-align: center;
        padding: 1.5rem;
        margin-top: 3rem;
        border-top: 1px solid var(--border-color);
        color: var(--text-light);
        font-size: 0.85rem;
    }
    
    /* Formularios más limpios */
    .stTextInput>div>div>input,
    .stSelectbox>div>div>select {
        border-radius: 8px;
        border: 1px solid var(--border-color);
    }
    
    /* Tabs profesionales */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        font-weight: 500;
    }
    
    /* Métricas más elegantes */
    [data-testid="stMetricValue"] {
        font-weight: 700;
        color: var(--primary-color);
    }
</style>
""", unsafe_allow_html=True)

# ==================== COMPONENTES CORPORATIVOS ====================

def mostrar_header_corporativo(titulo: str, subtitulo: str = None):
    """Muestra el header corporativo simple y profesional."""
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #0d47a1 0%, #1565c0 100%);
        color: white;
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    ">
        <h1 style="margin: 0; font-size: 1.8rem; font-weight: 700;">📋 {titulo}</h1>
        {"<p style='margin: 0.5rem 0 0 0; opacity: 0.9; font-size: 1rem;'>" + subtitulo + "</p>" if subtitulo else ""}
    </div>
    """, unsafe_allow_html=True)


def mostrar_footer():
    """Muestra el footer corporativo."""
    st.markdown("""
    <div style="
        text-align: center;
        padding: 1.5rem;
        margin-top: 3rem;
        border-top: 2px solid #e0e0e0;
        color: #666;
        font-size: 0.85rem;
    ">
        <p style="margin: 0;">Sistema de Gestión de Seguro Complementario</p>
        <p style="margin: 0.3rem 0 0 0;">© 2025 - Todos los derechos reservados</p>
    </div>
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
    """Menú de la barra lateral simplificado."""
    
    # Header limpio
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="margin: 0; color: #667eea;">🏢 Seguro</h2>
        <p style="margin: 0; color: #888; font-size: 0.9rem;">Complementario</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.sidebar.markdown("---")
    
    # Verificar si el admin está autenticado
    if 'admin_autenticado' not in st.session_state:
        st.session_state.admin_autenticado = False
    
    # Selector de modo
    modo = st.sidebar.radio(
        "Seleccione modo:",
        ["👤 Trabajador", "🔐 Administrador"],
        index=1 if st.session_state.admin_autenticado else 0,
        key="modo_selector"
    )
    
    if modo == "🔐 Administrador":
        if not st.session_state.admin_autenticado:
            # Mostrar login
            st.sidebar.markdown("#### Ingrese contraseña:")
            password = st.sidebar.text_input("Contraseña:", type="password", key="admin_pwd", label_visibility="collapsed")
            if st.sidebar.button("🔓 Ingresar", use_container_width=True):
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_autenticado = True
                    st.session_state.modo_admin = True
                    st.rerun()
                else:
                    st.sidebar.error("❌ Contraseña incorrecta")
        else:
            # Admin autenticado
            st.sidebar.success("✅ Sesión activa")
            st.session_state.modo_admin = True
            
            if st.sidebar.button("🚪 Cerrar Sesión", use_container_width=True):
                st.session_state.admin_autenticado = False
                st.session_state.modo_admin = False
                st.rerun()
    else:
        # Modo trabajador
        st.session_state.modo_admin = False
        st.sidebar.info("💼 Portal de trabajadores")
    
    st.sidebar.markdown("---")
    st.sidebar.caption("© 2024 - Sistema de Gestión")


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
            col1, col2, col3, col4, col5, col6, col7 = st.columns([1.5, 2.5, 1, 2, 1.5, 1, 0.5])
            with col1:
                st.write(f"**{carga['tipo']}**")
            with col2:
                st.write(carga['nombre'])
            with col3:
                sexo_icon = "👨" if carga.get('sexo') == "Masculino" else "👩"
                st.write(sexo_icon)
            with col4:
                st.write(carga['rut'])
            with col5:
                st.write(f"Nac: {formato_fecha_chile(carga['fecha_nacimiento'])}")
            with col6:
                st.write(f"{carga['edad']} años")
            with col7:
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
            sexo_carga = st.selectbox(
                "Sexo",
                options=["Masculino", "Femenino"]
            )
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
                'sexo': sexo_carga,
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
                    rut=datos['rut'],
                    nombre=datos['nombre'],
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
                        sexo=carga.get('sexo', 'No especificado'),
                        fecha_nacimiento=carga['fecha_nacimiento'],
                        edad=carga['edad']
                    )
                
                # Obtener registro completo para el email
                registro_completo = db.obtener_registro_con_cargas(registro_id)
                
                # Preparar datos para email
                datos_email = {
                    'rut': datos['rut'],
                    'nombre': datos['nombre'],
                    'email': datos['email'],
                    'banco': datos.get('banco'),
                    'tipo_cuenta': datos.get('tipo_cuenta'),
                    'numero_cuenta': datos.get('numero_cuenta')
                }
                cargas_email = registro_completo.get('cargas', []) if registro_completo else cargas
                
                # Intentar enviar correo
                smtp_configurado = os.getenv('SMTP_USER') and os.getenv('SMTP_PASSWORD')
                
                if smtp_configurado:
                    exito_email = enviar_correo_confirmacion(datos_email, cargas_email)
                else:
                    exito_email = simular_envio_correo(datos_email, cargas_email)
                
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
    mostrar_header_corporativo(
        "Registro de Seguro Complementario",
        None
    )
    
    if st.session_state.registro_completado:
        mostrar_confirmacion_final()
        mostrar_footer()
        return
    
    # Si ya tiene registro, mostrar portal de autoservicio
    if st.session_state.trabajador_validado and st.session_state.datos_trabajador.get('tiene_registro'):
        st.markdown('<p class="sub-header">Gestione sus cargas familiares</p>', unsafe_allow_html=True)
        portal_autoservicio()
        mostrar_footer()
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
    mostrar_header_corporativo(
        "Panel de Administración",
        "Gestión de empleados y registros del seguro complementario"
    )
    
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
                
                exitosos, fallidos, error_msg = db.importar_empleados_excel(temp_path)
                
                if exitosos > 0:
                    st.success(f"✅ {exitosos} empleados importados correctamente")
                if fallidos > 0:
                    st.warning(f"⚠️ {fallidos} registros fallidos")
                    if error_msg:
                        st.caption(f"Detalles: {error_msg}")
                if exitosos == 0 and fallidos == 0:
                    if error_msg:
                        st.error(f"❌ Error: {error_msg}")
                    else:
                        st.error("❌ No se pudo procesar el archivo")
                
                os.unlink(temp_path)
                if exitosos > 0:
                    st.rerun()
    
    with tab4:
        st.subheader("📊 Dashboard y Exportación")
        
        # Obtener estadísticas completas
        stats = db.obtener_estadisticas()
        pendientes = db.obtener_registros_pendientes_envio()
        cargas_nuevas = db.obtener_cargas_nuevas_pendientes()
        
        # ===== SECCIÓN 1: TARJETAS MÉTRICAS MODERNAS =====
        st.markdown("""
        <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 15px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            margin-bottom: 10px;
        }
        .metric-card.green { background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }
        .metric-card.orange { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .metric-card.blue { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .metric-card h2 { margin: 0; font-size: 2.5rem; font-weight: 700; }
        .metric-card p { margin: 5px 0 0 0; opacity: 0.9; font-size: 0.9rem; }
        </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h2>{stats.get('total_empleados', 0)}</h2>
                <p>👥 Empleados</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card green">
                <h2>{stats.get('total_registros', 0)}</h2>
                <p>📋 Registros</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card orange">
                <h2>{stats.get('total_cargas', 0)}</h2>
                <p>👨‍👩‍👧‍👦 Cargas Familiares</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            pct_enviado = 0
            if stats.get('total_registros', 0) > 0:
                pct_enviado = int((stats.get('registros_enviados', 0) / stats.get('total_registros', 1)) * 100)
            st.markdown(f"""
            <div class="metric-card blue">
                <h2>{pct_enviado}%</h2>
                <p>✅ Enviados a Aseguradora</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # ===== SECCIÓN 2: GRÁFICOS =====
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.markdown("### 📊 Distribución de Cargas")
            cargas_tipo = stats.get('cargas_por_tipo', {})
            if cargas_tipo:
                import plotly.express as px
                import pandas as pd
                
                df_tipos = pd.DataFrame({
                    'Tipo': list(cargas_tipo.keys()),
                    'Cantidad': list(cargas_tipo.values())
                })
                
                fig = px.pie(df_tipos, values='Cantidad', names='Tipo', 
                            color_discrete_sequence=['#667eea', '#764ba2', '#f5576c', '#38ef7d'],
                            hole=0.4)
                fig.update_layout(
                    showlegend=True,
                    legend=dict(orientation="h", yanchor="bottom", y=-0.2),
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos de cargas")
        
        with col_chart2:
            st.markdown("### 👨‍👧 Hijos por Género")
            hijos_sexo = stats.get('hijos_por_sexo', {})
            if hijos_sexo:
                import plotly.express as px
                import pandas as pd
                
                df_hijos = pd.DataFrame({
                    'Sexo': list(hijos_sexo.keys()),
                    'Cantidad': list(hijos_sexo.values())
                })
                
                colors = {'Masculino': '#4facfe', 'Femenino': '#f093fb'}
                fig = px.bar(df_hijos, x='Sexo', y='Cantidad', 
                            color='Sexo',
                            color_discrete_map=colors)
                fig.update_layout(
                    showlegend=False,
                    margin=dict(t=20, b=20, l=20, r=20),
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Sin datos de hijos")
        
        st.markdown("---")
        
        # ===== SECCIÓN 3: ESTADO DE ENVÍO =====
        st.markdown("### 📤 Estado de Envío a Aseguradora")
        
        col_status1, col_status2, col_status3 = st.columns(3)
        
        with col_status1:
            st.metric("⏳ Pendientes", len(pendientes), delta=None)
        with col_status2:
            st.metric("👶 Cargas Nuevas", len(cargas_nuevas), delta=None)
        with col_status3:
            st.metric("✅ Enviados", stats.get('registros_enviados', 0), delta=None)
        
        # Alertas
        if cargas_nuevas:
            st.warning(f"⚠️ Hay **{len(cargas_nuevas)}** carga(s) nueva(s) de trabajadores ya enviados.")
        
        if pendientes:
            st.success(f"✅ Hay **{len(pendientes)}** registro(s) listo(s) para enviar.")
            
            with st.expander("👁️ Ver registros pendientes"):
                for reg in pendientes[:10]:
                    st.write(f"• **{reg['nombre_trabajador']}** - RUT: {reg['rut_trabajador']}")
                if len(pendientes) > 10:
                    st.caption(f"... y {len(pendientes) - 10} más")
            
            st.markdown("#### ✉️ Enviar a la Aseguradora")
            
            email_aseguradora = st.text_input(
                "Correo de la Aseguradora",
                placeholder="seguros@ejemplo.cl",
                help="Ingrese el correo donde se enviará el listado"
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("📧 Enviar por Email", type="primary", disabled=not email_aseguradora):
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    lote = f"LOTE_{timestamp}"
                    archivo = f"exports/envio_seguro_{lote}.xlsx"
                    
                    if db.solo_exportar_pendientes(archivo):
                        if enviar_correo_aseguradora(email_aseguradora, archivo, len(pendientes), lote):
                            db.marcar_registros_enviados(lote)
                            st.success(f"✅ ¡Enviado a **{email_aseguradora}**!")
                            st.balloons()
                        else:
                            st.warning("⚠️ No se pudo enviar el correo.")
                    else:
                        st.error("❌ Error al generar archivo")
            
            with col_btn2:
                if st.button("📥 Solo Descargar"):
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    archivo = f"exports/descarga_{timestamp}.xlsx"
                    
                    if db.solo_exportar_pendientes(archivo):
                        st.success("✅ Archivo generado")
                        with open(archivo, 'rb') as f:
                            st.download_button("⬇️ Descargar", f, file_name=f"nuevas_altas_{timestamp}.xlsx")
        else:
            st.info("✅ Todo está al día. No hay registros pendientes.")
        
        st.markdown("---")
        
        # ===== SECCIÓN 4: HERRAMIENTAS =====
        with st.expander("📊 Exportar Reporte Completo"):
            if st.button("📊 Generar Reporte de TODO"):
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                archivo = f"exports/reporte_completo_{timestamp}.xlsx"
                if db.exportar_registros_excel(archivo):
                    st.success("✅ Generado")
                    with open(archivo, 'rb') as f:
                        st.download_button("⬇️ Descargar Completo", f, file_name=f"reporte_{timestamp}.xlsx")
        
        with st.expander("🔧 Herramientas Admin"):
            if st.button("🔄 Reiniciar Estado"):
                resultado = db.reiniciar_estado_envio()
                if resultado == -1:
                    st.error("❌ Error al reiniciar")
                elif resultado == 0:
                    st.info("ℹ️ No hay registros para reiniciar")
                else:
                    st.success(f"✅ {resultado} registro(s) reiniciado(s)")
                    st.rerun()


# ==================== MAIN ====================

def main():
    """Función principal de la aplicación - Layout de página única."""
    init_session_state()
    
    # Ya no usamos sidebar, todo en la página principal
    if 'admin_autenticado' not in st.session_state:
        st.session_state.admin_autenticado = False
    if 'modo_admin' not in st.session_state:
        st.session_state.modo_admin = False
    
    # Header con selector de modo
    col_logo, col_titulo, col_modo = st.columns([1, 4, 2])
    
    with col_logo:
        st.markdown("# 🏢")
    
    with col_titulo:
        st.markdown("### Seguro Complementario de Salud")
        st.caption("Sistema de Gestión de Cargas Familiares")
    
    with col_modo:
        # Selector de modo en el header
        modo_seleccionado = st.selectbox(
            "Modo:",
            ["👤 Trabajador", "🔐 Administrador"],
            index=1 if st.session_state.modo_admin else 0,
            key="modo_principal",
            label_visibility="collapsed"
        )
        
        if modo_seleccionado == "🔐 Administrador":
            if not st.session_state.admin_autenticado:
                with st.popover("🔐 Login Admin"):
                    password = st.text_input("Contraseña:", type="password", key="pwd_main")
                    if st.button("Ingresar", use_container_width=True):
                        if password == ADMIN_PASSWORD:
                            st.session_state.admin_autenticado = True
                            st.session_state.modo_admin = True
                            st.rerun()
                        else:
                            st.error("❌ Incorrecta")
            else:
                col_a, col_b = st.columns(2)
                with col_a:
                    st.success("✅ Admin")
                with col_b:
                    if st.button("Salir"):
                        st.session_state.admin_autenticado = False
                        st.session_state.modo_admin = False
                        st.rerun()
        else:
            st.session_state.modo_admin = False
            st.session_state.admin_autenticado = False
    
    st.markdown("---")
    
    # Mostrar vista según modo
    if st.session_state.modo_admin and st.session_state.admin_autenticado:
        vista_administrador()
    else:
        vista_trabajador()
    
    # Footer
    st.markdown("---")
    st.caption("© 2025-2026 | Sistema de Gestión de Seguro Complementario")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"❌ Error crítico: {str(e)}")
        logger.critical(f"Error crítico en aplicación: {e}", exc_info=True)

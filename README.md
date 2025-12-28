# � Sistema de Registro de Seguro Complementario

## Versión 2.0 - Diciembre 2024

Sistema web de autoservicio para que los trabajadores registren sus cargas familiares en el seguro complementario de la empresa.

---

## 📌 Descripción General

Este sistema reemplaza el **proceso manual en papel** por un sistema digital automatizado donde:

- **Los trabajadores** completan su registro de forma autónoma
- **El empleador** descarga los datos consolidados para enviar al seguro
- **Todo queda documentado** con respaldos automáticos

---

## 🚀 Funcionalidades Actuales

### 👤 Para el Trabajador

| Funcionalidad | Descripción |
|---------------|-------------|
| **Validación de RUT** | Solo empleados registrados en la base de datos pueden acceder |
| **Registro de datos de contacto** | Email validado para recibir confirmaciones |
| **Datos bancarios** | Banco, tipo y número de cuenta para reembolsos |
| **Registro de cargas** | Cónyuge e hijos con validación de edad (máx. 25 años para hijos) |
| **Portal de autoservicio** | Si ya tiene registro, puede: ver cargas, agregar nuevas, eliminar existentes |
| **Baja del seguro** | Puede solicitar baja inmediata del seguro |
| **Confirmación por email** | Recibe correo automático con resumen y fecha estimada de alta |

### 🔐 Para el Administrador (Empleador)

| Funcionalidad | Descripción |
|---------------|-------------|
| **Gestión de empleados** | Agregar manualmente o importar desde Excel |
| **Notificaciones** | Ve en tiempo real cuando un trabajador elimina cargas o se da de baja |
| **Ver registros** | Lista completa de trabajadores y sus cargas |
| **Exportar a Excel** | Genera archivo listo para enviar al seguro con todos los datos |

---

## 📊 Comparativa: Antes vs Ahora

### ❌ Proceso Anterior (Manual en Papel)

| Aspecto | Problema |
|---------|----------|
| **Formularios en papel** | Pérdida de documentos, letra ilegible, errores de transcripción |
| **Validación de RUT** | Sin validación automática, errores frecuentes |
| **Cálculo de edad** | Manual, propenso a errores |
| **Consolidación** | Recursos Humanos debe pasar todo a Excel manualmente |
| **Comunicación** | El trabajador no sabe si su registro fue recibido |
| **Modificaciones** | Requiere nuevo formulario y proceso completo |
| **Respaldo** | Archivos físicos que pueden perderse |
| **Tiempo RRHH** | ~15-30 minutos por trabajador (transcripción + verificación) |

### ✅ Proceso Actual (Sistema Digital)

| Aspecto | Solución |
|---------|----------|
| **Formulario digital** | Datos legibles, sin pérdidas, almacenados en base de datos |
| **Validación de RUT** | Algoritmo chileno con dígito verificador automático |
| **Cálculo de edad** | Automático basado en fecha de nacimiento |
| **Consolidación** | Exportación a Excel con un click |
| **Comunicación** | Email automático al trabajador con confirmación |
| **Modificaciones** | Autoservicio: agregar/eliminar cargas en cualquier momento |
| **Respaldo** | Base de datos SQLite + correos de respaldo |
| **Tiempo RRHH** | ~0 minutos por trabajador (solo revisión final) |

---

## ⏱️ Estimación de Ahorro de Tiempo

### Por cada trabajador registrado:

| Tarea | Tiempo Manual | Tiempo Sistema | Ahorro |
|-------|---------------|----------------|--------|
| Llenar formulario | 10 min | 5 min (trabajador) | 10 min RRHH |
| Validar RUT | 2 min | Automático | 2 min |
| Calcular edades | 2 min | Automático | 2 min |
| Transcribir a Excel | 10 min | Automático | 10 min |
| Verificar datos | 5 min | No necesario | 5 min |
| Comunicar al trabajador | 5 min | Automático | 5 min |
| **TOTAL por trabajador** | **34 min** | **0 min RRHH** | **34 min** |

### Proyección con 100 trabajadores:

| Métrica | Manual | Sistema | Ahorro |
|---------|--------|---------|--------|
| Tiempo total RRHH | 56 horas | 2 horas (supervisión) | **54 horas** |
| Riesgo de errores | Alto | Mínimo | Reducción ~95% |
| Costo en papel/tinta | $50,000+ | $0 | $50,000+ |

---

## � Arquitectura Técnica

```
📁 Proyecto Seguro Complementario/
├── 📄 main.py              # Aplicación principal Streamlit
├── 📄 config.py            # Configuración centralizada
├── 📄 .env                 # Variables de entorno (credenciales)
├── 📄 requirements.txt     # Dependencias Python
│
├── 📁 services/
│   ├── database.py         # Gestión SQLite
│   └── email_service.py    # Envío de correos
│
├── 📁 utils/
│   ├── validators.py       # Validación RUT, email, fechas
│   └── logger.py           # Sistema de logs
│
├── 📁 data/
│   ├── seguro_complementario.db   # Base de datos
│   ├── app.log                    # Logs de la aplicación
│   └── correos_enviados/          # Respaldo de correos (HTML)
│
└── 📁 exports/
    └── registros_seguro_*.xlsx    # Archivos exportados
```

---

## 🗃️ Estructura de la Base de Datos

### Tabla: `empleados`
Trabajadores autorizados de la empresa.

| Campo | Descripción |
|-------|-------------|
| rut | RUT del empleado (único) |
| nombre | Nombre completo |
| email | Correo electrónico |
| activo | Estado del empleado |

### Tabla: `registros_trabajador`
Registros de inscripción al seguro.

| Campo | Descripción |
|-------|-------------|
| rut_trabajador | RUT del trabajador |
| nombre_trabajador | Nombre completo |
| email | Correo para notificaciones |
| banco, tipo_cuenta, numero_cuenta | Datos bancarios |
| activo | Si está activo en el seguro |
| fecha_baja, motivo_baja | Datos de baja si aplica |

### Tabla: `cargas`
Cargas familiares registradas.

| Campo | Descripción |
|-------|-------------|
| tipo | "Cónyuge" o "Hijo" |
| rut | RUT de la carga |
| nombre | Nombre completo |
| fecha_nacimiento | Fecha de nacimiento |
| edad | Edad calculada |
| activo | Si está activo |

### Tabla: `notificaciones_admin`
Cambios que requieren atención del administrador.

| Campo | Descripción |
|-------|-------------|
| tipo | "ELIMINACION_CARGA" o "BAJA_SEGURO" |
| descripcion | Detalle del cambio |
| leida | Si fue revisada |

---

## � Validaciones Implementadas

### RUT Chileno
- ✅ Formato válido (puntos y guión)
- ✅ Algoritmo de dígito verificador
- ✅ Verificación contra base de empleados

### Email
- ✅ Formato correcto
- ✅ Dominios válidos (.cl, .com, etc.)

### Fechas
- ✅ Formato chileno DD/MM/AAAA
- ✅ Cálculo automático de edad
- ✅ Validación de edad máxima para hijos (25 años)

### Datos Bancarios
- ✅ Lista de bancos chilenos
- ✅ Tipos de cuenta válidos
- ✅ Número de cuenta numérico

---

## 📧 Sistema de Correos

### Configuración SMTP (Gmail)
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx  # Contraseña de aplicación
FROM_EMAIL=tu_correo@gmail.com
```

### Contenido del Correo de Confirmación
- Datos del trabajador
- Lista de cargas registradas
- Datos bancarios (si se ingresaron)
- Fecha estimada de alta (15 días hábiles)
- Instrucciones siguientes

---

## � Cómo Ejecutar

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
copy .env.example .env
# Editar .env con credenciales reales
```

### 3. Ejecutar aplicación
```bash
streamlit run main.py
```

### 4. Acceder
- **Trabajadores:** http://localhost:8501
- **Administrador:** Contraseña: `admin2024`

---

## 📋 Flujo de Uso

### Primer Uso (Trabajador Nuevo)

```
1. Trabajador ingresa RUT
   ↓
2. Sistema valida si es empleado
   ↓
3. Ingresa email y datos bancarios
   ↓
4. Agrega cónyuge e hijos
   ↓
5. Confirma y envía
   ↓
6. Recibe correo de confirmación
```

### Uso Posterior (Trabajador con Registro)

```
1. Trabajador ingresa RUT
   ↓
2. Sistema detecta registro existente
   ↓
3. Muestra Portal de Autoservicio:
   • Ver cargas actuales
   • Agregar nueva carga
   • Eliminar carga (notifica admin)
   • Solicitar baja (notifica admin)
```

### Administrador

```
1. Ingresa con contraseña
   ↓
2. Ve notificaciones pendientes
   ↓
3. Revisa/gestiona empleados
   ↓
4. Exporta datos a Excel para el seguro
```

---

## � Mejoras Futuras Planificadas

- [ ] Autenticación con usuario/contraseña para trabajadores
- [ ] Firma digital del registro
- [ ] Integración directa con API del seguro
- [ ] Dashboard con gráficos de estadísticas
- [ ] Notificaciones push/SMS
- [ ] Historial de cambios por trabajador
- [ ] Módulo de reportes avanzados
- [ ] Multi-empresa

---

## 📞 Soporte

Para consultas técnicas o mejoras, contactar al equipo de desarrollo.

---

**Versión:** 2.0  
**Última actualización:** Diciembre 2024  
**Desarrollado con:** Python, Streamlit, SQLite

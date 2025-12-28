# 📋 Manual de Usuario - Sistema de Seguro Complementario

## ¿Qué es este sistema?

Este sistema permite a los trabajadores inscribir a sus cargas familiares (cónyuge e hijos) en el seguro complementario de la empresa de forma digital, reemplazando el proceso en papel.

---

## 🎯 Beneficios del Sistema

### Antes (Proceso en papel)
- ❌ Formularios en papel que se pueden perder
- ❌ Letra ilegible y errores de transcripción
- ❌ RRHH debe pasar todo a Excel manualmente
- ❌ El trabajador no sabe si su registro fue recibido
- ❌ Modificaciones requieren nuevo formulario
- ❌ Tiempo: ~30 minutos por cada trabajador

### Ahora (Sistema digital)
- ✅ El trabajador ingresa sus datos directamente
- ✅ Validación automática de RUT y datos
- ✅ Exportación automática a Excel
- ✅ Correo de confirmación inmediato
- ✅ Modificaciones en cualquier momento
- ✅ Tiempo RRHH: ~0 minutos por trabajador

### 💰 Ahorro Estimado

| Cantidad de Trabajadores | Tiempo Manual | Tiempo con Sistema | Ahorro |
|--------------------------|---------------|-------------------|--------|
| 10 trabajadores | 5 horas | 15 minutos | **4.75 horas** |
| 50 trabajadores | 25 horas | 1 hora | **24 horas** |
| 100 trabajadores | 56 horas | 2 horas | **54 horas** |

---

# 👤 Guía para el TRABAJADOR

## Paso 1: Ingresar al Sistema

1. Abra su navegador web
2. Vaya a la dirección que le indicó RRHH
3. Verá la pantalla de bienvenida

## Paso 2: Validar su RUT

1. Ingrese su RUT en el campo indicado
2. Puede escribirlo con o sin puntos (ejemplo: `12345678-9` o `12.345.678-9`)
3. Presione **"🔍 Validar RUT"**

**¿Qué puede pasar?**
- ✅ Si su RUT está registrado, pasará al siguiente paso
- ❌ Si aparece error, contacte a RRHH para que lo agreguen al sistema

## Paso 3: Datos de Contacto

1. **Correo electrónico:** Ingrese su email personal o laboral
   - Aquí recibirá la confirmación de su registro
   - Asegúrese de escribirlo correctamente

2. **Datos bancarios (opcional):**
   - Banco
   - Tipo de cuenta (corriente, vista, ahorro)
   - Número de cuenta
   - *Estos datos se usan para reembolsos del seguro*

3. Presione **"💾 Guardar y Continuar"**

## Paso 4: Agregar Cargas Familiares

### Para agregar CÓNYUGE:
1. Seleccione "Cónyuge"
2. Ingrese:
   - RUT del cónyuge
   - Nombre completo
   - Fecha de nacimiento (calendario en formato DD/MM/AAAA)
3. Presione **"➕ Agregar Carga"**

### Para agregar HIJOS:
1. Seleccione "Hijo/a"
2. Ingrese los datos del hijo
3. Presione **"➕ Agregar Carga"**
4. **Repita** para cada hijo adicional

**Importante sobre los hijos:**
- Solo pueden registrarse hijos de hasta 25 años
- Si un hijo tiene más de 25 años, no podrá agregarlo

### Cuando termine de agregar cargas:
Presione **"✅ Finalizar Registro"**

## Paso 5: Confirmar y Enviar

1. Revise el resumen de sus datos
2. Verifique que todo esté correcto
3. Marque la casilla de confirmación
4. Presione **"📤 Enviar Registro"**

**¡Listo!** Recibirá un correo de confirmación con:
- Sus datos registrados
- Lista de cargas familiares
- Fecha estimada de alta (15 días hábiles)

---

## 🔄 Si Ya Tiene Registro (Portal de Autoservicio)

Si usted ya se registró anteriormente, al ingresar su RUT verá el **Portal de Autoservicio** con estas opciones:

### 👁️ Ver Mis Cargas
Muestra la lista de sus cargas familiares activas.

### ➕ Agregar Nueva Carga
Si olvidó registrar un hijo o se casó recientemente:
1. Vaya a esta pestaña
2. Complete los datos
3. Se agregará automáticamente

### ❌ Eliminar Carga
Si necesita eliminar una carga (por ejemplo, divorcio o hijo que cumplió 26 años):
1. Vaya a esta pestaña
2. Presione el botón "🗑️ Eliminar" junto a la carga
3. La carga se eliminará y **RRHH será notificado** para informar al seguro

### 🚫 Baja del Seguro
Si desea darse de baja completamente del seguro:
1. Vaya a esta pestaña
2. Lea las advertencias (es irreversible)
3. Escriba el motivo (opcional)
4. Marque la confirmación
5. Presione el botón de baja

**Importante:** La baja es inmediata y RRHH será notificado automáticamente.

---

# 🔐 Guía para el ADMINISTRADOR (RRHH)

## Acceso al Panel de Administración

1. En la barra lateral izquierda, busque **"🔐 Acceso Administrador"**
2. Ingrese la contraseña: `admin2024`
3. Presione **"Ingresar"**

## Pestaña: 🔔 Notificaciones

Aquí verá los cambios que los trabajadores han realizado:
- **Eliminaciones de cargas:** Cuando un trabajador elimina un hijo o cónyuge
- **Bajas de seguro:** Cuando un trabajador se da de baja completamente

**¿Qué hacer?**
1. Revise cada notificación
2. Informe los cambios a la compañía de seguros
3. Marque como leída presionando "✓"

## Pestaña: 📊 Registros

Muestra todos los trabajadores que se han registrado y sus cargas.

Para cada trabajador puede ver:
- Email de contacto
- Datos bancarios
- Lista de cargas familiares
- Estado del email de confirmación

## Pestaña: 👥 Empleados

### Agregar empleado individual:
1. Ingrese RUT, Nombre y Email
2. Presione **"➕ Agregar Empleado"**

### Importar desde Excel:
1. Prepare un archivo Excel con columnas: **RUT**, **Nombre**, **Email**
2. Suba el archivo
3. Presione **"📥 Importar Empleados"**
4. El sistema agregará todos los empleados automáticamente

**Importante:** Solo los empleados agregados aquí podrán acceder al sistema de registro.

## Pestaña: 📥 Exportar

Para generar el archivo Excel y enviarlo a la compañía de seguros:

1. Presione **"📊 Generar Reporte Excel"**
2. Se creará un archivo con dos hojas:
   - **Trabajadores:** Datos de contacto y bancarios
   - **Cargas Familiares:** Todas las cargas con fechas de nacimiento
3. Presione **"⬇️ Descargar Excel"**
4. Envíe este archivo a la compañía de seguros

---

## ❓ Preguntas Frecuentes

### ¿Qué hago si mi RUT no está registrado?
Contacte a RRHH para que lo agreguen a la base de datos de empleados.

### ¿Puedo corregir un error después de enviar?
Sí. Ingrese nuevamente con su RUT y use el Portal de Autoservicio para eliminar la carga incorrecta y agregar la correcta.

### ¿Cuánto tiempo tarda en activarse el seguro?
Aproximadamente 15 días hábiles desde que completó el registro.

### ¿No me llegó el correo de confirmación?
1. Revise su carpeta de spam/correo no deseado
2. Verifique que escribió bien su email
3. Contacte a RRHH si el problema persiste

### ¿Puedo agregar un hijo mayor de 25 años?
No. La edad máxima para hijos es 25 años según las condiciones del seguro.

### ¿Qué pasa si elimino una carga por error?
Puede volver a agregarla inmediatamente desde el Portal de Autoservicio.

---

## 📞 Soporte

Si tiene problemas con el sistema, contacte al departamento de Recursos Humanos.

---

*Manual actualizado: Diciembre 2025*

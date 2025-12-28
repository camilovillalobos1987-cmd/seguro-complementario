# 🚀 Guía de Despliegue en Streamlit Cloud

## Paso 1: Crear Repositorio en GitHub

1. Ve a [github.com](https://github.com) e inicia sesión
2. Click en el botón verde **"New"** (Nuevo repositorio)
3. Nombre: `seguro-complementario` (o el que prefieras)
4. Selecciona **"Private"** (Privado) para que solo tú lo veas
5. Click en **"Create repository"**

## Paso 2: Subir el Proyecto a GitHub

### Opción A: Usando GitHub Desktop (Más fácil)

1. Descarga [GitHub Desktop](https://desktop.github.com/)
2. Inicia sesión con tu cuenta
3. File > Add Local Repository
4. Selecciona la carpeta del proyecto
5. Commit y Push

### Opción B: Usando Git por línea de comandos

Abre PowerShell en la carpeta del proyecto y ejecuta:

```powershell
# Inicializar repositorio (si no existe)
git init

# Agregar todos los archivos
git add .

# Crear commit
git commit -m "Primera version del sistema de seguro complementario"

# Conectar con GitHub (reemplaza TU_USUARIO y TU_REPO)
git remote add origin https://github.com/TU_USUARIO/seguro-complementario.git

# Subir
git branch -M main
git push -u origin main
```

## Paso 3: Conectar con Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Click en **"Sign in with GitHub"**
3. Autoriza el acceso
4. Click en **"New app"**
5. Selecciona:
   - Repository: `TU_USUARIO/seguro-complementario`
   - Branch: `main`
   - Main file path: `main.py`
6. Click en **"Deploy!"**

## Paso 4: Configurar Secretos (IMPORTANTE)

Una vez desplegada la app:

1. Ve a tu app en Streamlit Cloud
2. Click en los 3 puntos (**⋮**) > **Settings**
3. Busca la sección **"Secrets"**
4. Agrega este contenido (con tus datos reales):

```toml
[smtp]
host = "smtp.gmail.com"
port = 587
user = "tu_correo@gmail.com"
password = "xxxx xxxx xxxx xxxx"
from_email = "tu_correo@gmail.com"

[admin]
password = "admin2024"
```

5. Click en **"Save"**

## Paso 5: ¡Listo!

Tu aplicación estará disponible en una URL como:
```
https://tu-usuario-seguro-complementario.streamlit.app
```

Comparte esta URL con las personas que quieras que prueben el sistema.

---

## ⚠️ Notas Importantes

### Sobre la Base de Datos
- En modo prueba, la base de datos SQLite funcionará pero se reiniciará si la app se "duerme" (después de varios días sin uso)
- Para producción, migraremos a una base de datos en la nube

### Sobre los Correos
- Configura los secretos SMTP como se indica arriba para que funcionen los correos

### Sobre la Seguridad
- El repositorio está en **Privado**, solo tú puedes verlo
- Los secretos se configuran aparte, no se suben a GitHub

---

## 🔄 Actualizar la Aplicación

Cuando hagas cambios en el código:

1. Guarda los cambios
2. En Git:
```powershell
git add .
git commit -m "Descripcion del cambio"
git push
```
3. Streamlit Cloud detectará el cambio y actualizará automáticamente

---

*¿Problemas? Contacta al equipo de desarrollo.*

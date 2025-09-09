# Organizador Inteligente

Una aplicación profesional para organizar archivos de manera automática e inteligente.

## Características

- **Clasificación Inteligente**: Organiza archivos por tipo, tamaño, fecha o reglas personalizadas
- **Detección de Carpetas Vacías**: Encuentra y elimina carpetas sin contenido
- **Historial Completo**: Revisa y restaura cualquier acción realizada
- **Interfaz Profesional**: Diseño moderno e intuitivo
- **Autenticación Segura**: Sistema de login y registro de usuarios

## Instalación

1. **Configurar MySQL:**
   - Asegúrate de tener MySQL instalado y ejecutándose
   - Abre phpMyAdmin o la consola de MySQL
   - Ejecuta el script `database_schema.sql` para crear las tablas

2. **Configurar la base de datos:**
   - Edita el archivo `db_config.py`
   - Modifica las credenciales de MySQL (usuario y contraseña)
   - Ajusta la configuración según tu instalación de MySQL

3. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación:**
```bash
python main.py
```

## Configuración de Base de Datos

### Requisitos:
- MySQL 5.7+ o MariaDB 10.2+
- phpMyAdmin (opcional, para administración web)

### Pasos de configuración:

1. **Crear la base de datos:**
   ```sql
   CREATE DATABASE organizador;
   ```

2. **Ejecutar el script de creación de tablas:**
   - Abre `database_schema.sql` en phpMyAdmin
   - Ejecuta todo el script

3. **Configurar credenciales:**
   - Edita `db_config.py`
   - Cambia `user` y `password` por tus credenciales de MySQL

### Estructura de la base de datos:
- **Usuarios**: Información de usuarios y autenticación
- **Historial**: Registro de acciones realizadas
- **Reglas**: Reglas de clasificación personalizadas
- **Configuraciones**: Configuraciones específicas por usuario

## Uso

1. **Registro/Login**: Crea una cuenta o inicia sesión
2. **Seleccionar Carpetas**: Elige la carpeta fuente y destino (opcional)
3. **Clasificar**: Usa clasificación básica o avanzada con reglas personalizadas
4. **Gestionar Carpetas Vacías**: Detecta y elimina carpetas sin contenido
5. **Revisar Historial**: Ve el historial de acciones y restaura si es necesario

## Funcionalidades

### Clasificación Básica
Organiza archivos por tipo de extensión en carpetas predefinidas.

### Clasificación Avanzada
Usa reglas personalizadas basadas en:
- Extensiones de archivo
- Tamaño mínimo/máximo
- Rango de fechas
- Destino personalizado

### Gestión de Carpetas Vacías
- Detecta carpetas sin contenido
- Excluye carpetas del sistema
- Elimina de forma segura

### Historial y Restauración
- Registra todas las acciones
- Permite restaurar cambios
- Mantiene trazabilidad completa

## Estructura del Proyecto

```
organizador_inteligente/
├── main.py              # Punto de entrada
├── auth.py              # Autenticación
├── ui.py                # Interfaz de usuario
├── models.py            # Modelos de datos
├── services.py          # Lógica de negocio
├── repositories.py      # Acceso a datos
├── config.py            # Configuración
└── requirements.txt     # Dependencias
```

## Tecnologías

- **Flet**: Framework de UI moderno
- **SQLite**: Base de datos local
- **Python 3.8+**: Lenguaje de programación

## Licencia

Este proyecto está bajo la Licencia MIT.

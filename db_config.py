# organizador_inteligente/db_config.py
# -------------------------------------------------------------
# Configuración de la base de datos MySQL
# Modifica estos valores según tu configuración de MySQL
# -------------------------------------------------------------

# Configuración de la base de datos MySQL
DB_CONFIG = {
    'host': '127.0.0.1',        # IP del servidor MySQL
    'database': 'organizador',   # Nombre de la base de datos
    'user': 'root',             # Usuario de MySQL
    'password': '',             # Contraseña de MySQL (cambiar por tu contraseña)
    'port': 3306,               # Puerto de MySQL
    'charset': 'utf8mb4',       # Codificación de caracteres
    'collation': 'utf8mb4_unicode_ci'  # Collation
}

# Instrucciones:
# 1. Asegúrate de que MySQL esté ejecutándose en tu sistema
# 2. Crea la base de datos 'organizador' si no existe
# 3. Ejecuta los scripts SQL proporcionados para crear las tablas
# 4. Modifica 'user' y 'password' con tus credenciales de MySQL
# 5. Si usas un puerto diferente, modifica 'port'



# organizador_inteligente/database.py
# -------------------------------------------------------------
# Configuración y conexión a la base de datos MySQL
# -------------------------------------------------------------

import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import hashlib
from db_config import DB_CONFIG

class DatabaseManager:
    """Maneja la conexión y operaciones con la base de datos MySQL."""
    
    def __init__(self):
        self.connection = None
        self.config = DB_CONFIG
    
    def connect(self):
        """Establece conexión con la base de datos."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print("Conexión exitosa a MySQL")
                return True
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return False
    
    def disconnect(self):
        """Cierra la conexión con la base de datos."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Conexión a MySQL cerrada")
    
    def execute_query(self, query: str, params: Tuple = None, fetch: bool = False):
        """Ejecuta una consulta SQL."""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.lastrowid
            
            cursor.close()
            return result
        except Error as e:
            print(f"Error ejecutando consulta: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Obtiene un usuario por su correo electrónico."""
        query = "SELECT * FROM Usuarios WHERE correo_electronico = %s"
        result = self.execute_query(query, (email,), fetch=True)
        return result[0] if result else None
    
    def create_user(self, username: str, cedula: str, email: str, password: str) -> bool:
        """Crea un nuevo usuario en la base de datos."""
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        query = """
        INSERT INTO Usuarios (nombre_usuario, cedula, correo_electronico, contrasena_hash, fecha_registro)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.execute_query(query, (username, cedula, email, hashed_password, datetime.now().date()))
            return True
        except Error as e:
            print(f"Error creando usuario: {e}")
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Autentica un usuario con email y contraseña."""
        user = self.get_user_by_email(email)
        if user:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if user['contrasena_hash'] == hashed_password:
                return user
        return None
    
    def get_user_rules(self, user_id: int) -> List[Dict]:
        """Obtiene las reglas de un usuario."""
        query = "SELECT * FROM Reglas WHERE id_usuario = %s ORDER BY id_regla"
        return self.execute_query(query, (user_id,), fetch=True) or []
    
    def create_rule(self, user_id: int, rule_data: Dict) -> bool:
        """Crea una nueva regla para un usuario."""
        query = """
        INSERT INTO Reglas (id_usuario, nombre, destino_subcarpeta, extensiones, 
                           tam_min_kb, tam_max_kb, fecha_desde, fecha_hasta)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        try:
            self.execute_query(query, (
                user_id,
                rule_data['nombre'],
                rule_data['destino_subcarpeta'],
                json.dumps(rule_data['extensiones']),
                rule_data.get('tam_min_kb'),
                rule_data.get('tam_max_kb'),
                rule_data.get('fecha_desde'),
                rule_data.get('fecha_hasta')
            ))
            return True
        except Error as e:
            print(f"Error creando regla: {e}")
            return False
    
    def update_rule(self, rule_id: int, user_id: int, rule_data: Dict) -> bool:
        """Actualiza una regla existente."""
        query = """
        UPDATE Reglas SET nombre = %s, destino_subcarpeta = %s, extensiones = %s,
                         tam_min_kb = %s, tam_max_kb = %s, fecha_desde = %s, fecha_hasta = %s
        WHERE id_regla = %s AND id_usuario = %s
        """
        try:
            self.execute_query(query, (
                rule_data['nombre'],
                rule_data['destino_subcarpeta'],
                json.dumps(rule_data['extensiones']),
                rule_data.get('tam_min_kb'),
                rule_data.get('tam_max_kb'),
                rule_data.get('fecha_desde'),
                rule_data.get('fecha_hasta'),
                rule_id,
                user_id
            ))
            return True
        except Error as e:
            print(f"Error actualizando regla: {e}")
            return False
    
    def delete_rule(self, rule_id: int, user_id: int) -> bool:
        """Elimina una regla."""
        query = "DELETE FROM Reglas WHERE id_regla = %s AND id_usuario = %s"
        try:
            self.execute_query(query, (rule_id, user_id))
            return True
        except Error as e:
            print(f"Error eliminando regla: {e}")
            return False
    
    def add_history_record(self, user_id: int, action_type: str, details: Dict, 
                          quarantine_path: str = None) -> bool:
        """Agrega un registro al historial."""
        query = """
        INSERT INTO Historial (id_usuario, tipo, fecha, detalle, ruta_cuarentena)
        VALUES (%s, %s, %s, %s, %s)
        """
        try:
            self.execute_query(query, (
                user_id,
                action_type,
                datetime.now(),
                json.dumps(details),
                quarantine_path
            ))
            return True
        except Error as e:
            print(f"Error agregando historial: {e}")
            return False
    
    def get_user_history(self, user_id: int, limit: int = 200) -> List[Dict]:
        """Obtiene el historial de un usuario."""
        query = """
        SELECT * FROM Historial 
        WHERE id_usuario = %s 
        ORDER BY fecha DESC 
        LIMIT %s
        """
        return self.execute_query(query, (user_id, limit), fetch=True) or []
    
    def get_user_config(self, user_id: int, key: str) -> Optional[str]:
        """Obtiene una configuración específica de un usuario."""
        query = "SELECT valor FROM Configuraciones WHERE id_usuario = %s AND clave = %s"
        result = self.execute_query(query, (user_id, key), fetch=True)
        return result[0]['valor'] if result else None
    
    def set_user_config(self, user_id: int, key: str, value: str) -> bool:
        """Establece una configuración para un usuario."""
        query = """
        INSERT INTO Configuraciones (id_usuario, clave, valor, fecha_modificacion)
        VALUES (%s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE valor = %s, fecha_modificacion = %s
        """
        try:
            now = datetime.now()
            self.execute_query(query, (user_id, key, value, now, value, now))
            return True
        except Error as e:
            print(f"Error estableciendo configuración: {e}")
            return False

# Instancia global de la base de datos
db_manager = DatabaseManager()

# organizador_inteligente/repositories.py
# -------------------------------------------------------------
# Repositorios de datos (MySQL)
# -------------------------------------------------------------

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from database import db_manager

class RepositorioHistorial:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def registrar(self, tipo: str, detalle: Dict[str, Any],
                 ruta_origen: Optional[str] = None,
                 ruta_destino: Optional[str] = None,
                 ruta_cuarentena: Optional[str] = None):
        """Registra una acción en la base de datos."""
        # Mapear tipos de SQLite a MySQL
        tipo_mysql = "organizar" if tipo == "clasificacion" else "eliminar_carpetas"
        
        # Agregar rutas al detalle si están disponibles
        if ruta_origen:
            detalle["ruta_origen"] = ruta_origen
        if ruta_destino:
            detalle["ruta_destino"] = ruta_destino
            
        db_manager.add_history_record(
            self.user_id, 
            tipo_mysql, 
            detalle, 
            ruta_cuarentena
        )

    def listar(self, limite: int = 200) -> List[Dict[str, Any]]:
        """Lista las acciones registradas, ordenadas por fecha descendente."""
        historial = db_manager.get_user_history(self.user_id, limite)
        
        salida = []
        for h in historial:
            # Mapear tipos de MySQL a SQLite para compatibilidad
            tipo_sqlite = "clasificacion" if h["tipo"] == "organizar" else "carpeta_vacia"
            
            detalle = json.loads(h["detalle"]) if h["detalle"] else {}
            
            salida.append({
                "id": h["id_accion"],
                "fecha": h["fecha"].strftime("%Y-%m-%d %H:%M:%S"),
                "tipo": tipo_sqlite,
                "detalle": detalle,
                "ruta_origen": detalle.get("ruta_origen"),
                "ruta_destino": detalle.get("ruta_destino"),
                "ruta_cuarentena": h["ruta_cuarentena"],
            })
        return salida

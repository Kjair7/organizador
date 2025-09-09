# organizador_inteligente/services.py
# -------------------------------------------------------------
# Servicios de negocio (clasificación, reglas, carpetas)
# -------------------------------------------------------------

import json
import os
import shutil
import time
import threading
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from config import CATEGORIAS, EXCLUSIONES_POR_DEFECTO
from models import ReglaClasificacion
from repositories import RepositorioHistorial
from database import db_manager

class ServicioReglas:
    def __init__(self, user_id: int):
        self.user_id = user_id

    def cargar(self) -> List[ReglaClasificacion]:
        """Carga las reglas de clasificación desde la base de datos."""
        reglas_db = db_manager.get_user_rules(self.user_id)
        
        if not reglas_db:
            # Crear reglas de ejemplo si no hay ninguna
            ejemplo = [
                {
                    "nombre": "Imágenes grandes recientes",
                    "destino_subcarpeta": "Imagenes_Grandes_Recientes",
                    "extensiones": ["jpg", "png", "jpeg"],
                    "tam_min_kb": 1500,
                    "fecha_desde": datetime.now().replace(day=1).strftime("%Y-%m-%d"),
                },
                {
                    "nombre": "Documentos antiguos",
                    "destino_subcarpeta": "Documentos_Antiguos",
                    "extensiones": ["pdf", "docx", "pptx"],
                    "fecha_hasta": (datetime.now().replace(year=datetime.now().year - 1).strftime("%Y-%m-%d")),
                },
            ]
            
            for regla_data in ejemplo:
                db_manager.create_rule(self.user_id, regla_data)
            
            # Recargar las reglas
            reglas_db = db_manager.get_user_rules(self.user_id)
        
        reglas = []
        for r in reglas_db:
            regla = ReglaClasificacion(
                nombre=r["nombre"],
                destino_subcarpeta=r["destino_subcarpeta"],
                extensiones=json.loads(r["extensiones"]) if r["extensiones"] else [],
                tam_min_kb=r["tam_min_kb"],
                tam_max_kb=r["tam_max_kb"],
                fecha_desde=r["fecha_desde"].strftime("%Y-%m-%d") if r["fecha_desde"] else None,
                fecha_hasta=r["fecha_hasta"].strftime("%Y-%m-%d") if r["fecha_hasta"] else None,
            )
            reglas.append(regla)
        
        return reglas

    def guardar(self, reglas: List[ReglaClasificacion]):
        """Guarda las reglas de clasificación en la base de datos."""
        # Eliminar reglas existentes
        reglas_existentes = db_manager.get_user_rules(self.user_id)
        for regla_existente in reglas_existentes:
            db_manager.delete_rule(regla_existente["id_regla"], self.user_id)
        
        # Crear nuevas reglas
        for regla in reglas:
            regla_data = {
                "nombre": regla.nombre,
                "destino_subcarpeta": regla.destino_subcarpeta,
                "extensiones": regla.extensiones,
                "tam_min_kb": regla.tam_min_kb,
                "tam_max_kb": regla.tam_max_kb,
                "fecha_desde": regla.fecha_desde,
                "fecha_hasta": regla.fecha_hasta,
            }
            db_manager.create_rule(self.user_id, regla_data)

class ServicioClasificacion:
    def __init__(self, repo_historial: RepositorioHistorial):
        self.repo = repo_historial

    def _categoria_por_extension(self, ext: str) -> Optional[str]:
        """Determina la categoría basada en la extensión del archivo."""
        ext = ext.lower().lstrip(".")
        for cat, lista in CATEGORIAS.items():
            if ext in lista:
                return cat
        return None

    def clasificar_basico(self, fuente: Path, destino_base: Optional[Path] = None, progreso_cb: Optional[Callable[[float], None]] = None) -> Dict[str, Any]:
        """Clasifica archivos de manera básica por tipo de extensión."""
        if destino_base is None:
            destino_base = fuente
        movidos = []
        total = sum(1 for _ in fuente.rglob("*") if _.is_file())
        procesados = 0
        for archivo in fuente.rglob("*"):
            if archivo.is_file():
                procesados += 1
                if progreso_cb and procesados % 25 == 0:
                    progreso_cb(min(0.95, procesados / max(1, total)))
                categoria = self._categoria_por_extension(archivo.suffix)
                if categoria is None:
                    continue
                destino = destino_base / categoria
                destino.mkdir(exist_ok=True)
                try:
                    nuevo = destino / archivo.name
                    if nuevo.exists():
                        nuevo = destino / f"{archivo.stem}_{int(time.time())}{archivo.suffix}"
                    shutil.move(str(archivo), str(nuevo))
                    movidos.append((str(archivo), str(nuevo)))
                except Exception:
                    pass
        detalle = {"archivos_movidos": len(movidos)}
        self.repo.registrar("clasificacion", detalle)
        if progreso_cb:
            progreso_cb(1.0)
        return detalle

    def clasificar_avanzado(self, fuente: Path, reglas: List[ReglaClasificacion], destino_base: Optional[Path] = None, progreso_cb: Optional[Callable[[float], None]] = None) -> Dict[str, Any]:
        """Clasifica archivos usando reglas avanzadas con fallback a clasificación básica."""
        if destino_base is None:
            destino_base = fuente
        movidos = []
        total = sum(1 for _ in fuente.rglob("*") if _.is_file())
        procesados = 0
        for archivo in fuente.rglob("*"):
            if not archivo.is_file():
                continue
            procesados += 1
            if progreso_cb and procesados % 25 == 0:
                progreso_cb(min(0.95, procesados / max(1, total)))
            aplicado = False
            for regla in reglas:
                if regla.coincide(archivo):
                    destino = destino_base / regla.destino_subcarpeta
                    destino.mkdir(exist_ok=True)
                    try:
                        nuevo = destino / archivo.name
                        if nuevo.exists():
                            nuevo = destino / f"{archivo.stem}_{int(time.time())}{archivo.suffix}"
                        shutil.move(str(archivo), str(nuevo))
                        movidos.append((str(archivo), str(nuevo), regla.nombre))
                        aplicado = True
                        break
                    except Exception:
                        pass
            if not aplicado:
                categoria = self._categoria_por_extension(archivo.suffix)
                if categoria is None:
                    continue
                destino = destino_base / categoria
                destino.mkdir(exist_ok=True)
                try:
                    nuevo = destino / archivo.name
                    if nuevo.exists():
                        nuevo = destino / f"{archivo.stem}_{int(time.time())}{archivo.suffix}"
                    shutil.move(str(archivo), str(nuevo))
                    movidos.append((str(archivo), str(nuevo), "basico"))
                except Exception:
                    pass
        detalle = {"archivos_movidos": len(movidos), "reglas": [r.nombre for r in reglas]}
        self.repo.registrar("clasificacion", detalle)
        if progreso_cb:
            progreso_cb(1.0)
        return detalle

class ServicioCarpetas:
    def __init__(self, repo_historial: RepositorioHistorial):
        self.repo = repo_historial

    def detectar_vacias(self, carpeta: Path, exclusiones: Optional[List[str]] = None) -> List[Path]:
        """Detecta carpetas vacías en la ruta especificada, excluyendo las definidas."""
        exclusiones = set(exclusiones or []) | EXCLUSIONES_POR_DEFECTO
        candidatas = []
        for dirpath, dirnames, filenames in os.walk(carpeta, topdown=False):
            p = Path(dirpath)
            if p == carpeta:
                continue
            if p.name in exclusiones:
                continue
            if len(dirnames) == 0 and len(filenames) == 0:
                candidatas.append(p)
        return candidatas

    def eliminar_vacias(self, carpetas: List[Path], progreso_cb: Optional[Callable[[float], None]] = None) -> List[Path]:
        """Elimina carpetas vacías y registra la acción."""
        eliminadas = []
        total = len(carpetas)
        procesados = 0
        for c in carpetas:
            try:
                shutil.rmtree(str(c))
                eliminadas.append(c)
                self.repo.registrar(
                    "carpeta_vacia",
                    {"accion": "eliminar"},
                    ruta_origen=str(c),
                )
                procesados += 1
                if progreso_cb and procesados % 10 == 0:
                    progreso_cb(min(0.95, procesados / max(1, total)))
            except Exception:
                pass
        if progreso_cb:
            progreso_cb(1.0)
        return eliminadas

    def restaurar(self, ruta_cuarentena: Path, destino_padre: Path) -> bool:
        """Restaura una carpeta de cuarentena al destino especificado."""
        try:
            destino = destino_padre / ruta_cuarentena.name
            i = 1
            while destino.exists():
                destino = destino_padre / f"{ruta_cuarentena.name}_{i}"
                i += 1
            shutil.move(str(ruta_cuarentena), str(destino))
            self.repo.registrar(
                "carpeta_vacia",
                {"accion": "restaurar"},
                ruta_origen=str(destino),
                ruta_cuarentena=str(ruta_cuarentena),
            )
            return True
        except Exception:
            return False

class CoordinadorTareas:
    def __init__(self):
        self.hilo: Optional[threading.Thread] = None
        self.cancelar = threading.Event()

    def en_ejecucion(self) -> bool:
        """Verifica si hay una tarea en ejecución."""
        return self.hilo is not None and self.hilo.is_alive()

    def ejecutar(self, funcion, *args, **kwargs):
        """Ejecuta una tarea en un hilo separado."""
        if self.en_ejecucion():
            raise RuntimeError("Ya hay una tarea en ejecución")
        self.cancelar.clear()
        self.hilo = threading.Thread(target=funcion, args=args, kwargs=kwargs, daemon=True)
        self.hilo.start()

    def detener(self):
        """Detiene la tarea actual."""
        self.cancelar.set()

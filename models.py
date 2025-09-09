# organizador_inteligente/models.py
# -------------------------------------------------------------
# Modelos de dominio
# -------------------------------------------------------------

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

@dataclass
class ReglaClasificacion:
    nombre: str
    destino_subcarpeta: str
    extensiones: List[str]
    tam_min_kb: Optional[int] = None
    tam_max_kb: Optional[int] = None
    fecha_desde: Optional[str] = None  # ISO "YYYY-MM-DD"
    fecha_hasta: Optional[str] = None

    def coincide(self, archivo: Path) -> bool:
        """Verifica si el archivo coincide con la regla."""
        try:
            if not archivo.is_file():
                return False
            ext = archivo.suffix.lower().lstrip(".")
            if self.extensiones and ext not in [e.lower().lstrip(".") for e in self.extensiones]:
                return False

            tam_kb = int(archivo.stat().st_size / 1024)
            if self.tam_min_kb is not None and tam_kb < self.tam_min_kb:
                return False
            if self.tam_max_kb is not None and tam_kb > self.tam_max_kb:
                return False

            mtime = datetime.fromtimestamp(archivo.stat().st_mtime)
            if self.fecha_desde:
                if mtime.date() < datetime.fromisoformat(self.fecha_desde).date():
                    return False
            if self.fecha_hasta:
                if mtime.date() > datetime.fromisoformat(self.fecha_hasta).date():
                    return False
            return True
        except Exception:
            return False

# organizador_inteligente/config.py
# -------------------------------------------------------------
# Configuraciones y constantes del aplicativo
# -------------------------------------------------------------

from pathlib import Path

APP_NOMBRE = "Organizador Inteligente"
APP_CARPETA_DATOS = ".organizador_inteligente"  # en HOME

def ruta_home() -> Path:
    """Obtiene la ruta del directorio home del usuario."""
    return Path.home()

def ruta_datos_app() -> Path:
    """Obtiene o crea la ruta de datos de la aplicación."""
    base = ruta_home() / APP_CARPETA_DATOS
    base.mkdir(parents=True, exist_ok=True)
    (base / "cuarentena").mkdir(parents=True, exist_ok=True)
    (base / "config").mkdir(parents=True, exist_ok=True)
    return base

def ruta_bd() -> Path:
    """Obtiene la ruta de la base de datos SQLite."""
    return ruta_datos_app() / "historial.sqlite3"

def ruta_reglas_json() -> Path:
    """Obtiene la ruta del archivo JSON de reglas."""
    return ruta_datos_app() / "config" / "reglas.json"

CATEGORIAS = {
    "documentos_pdf": ["pdf"],
    "documentos_word": ["doc", "docx"],
    "documentos_texto": ["txt", "rtf"],
    "hojas_calculo": ["xls", "xlsx", "csv"],
    "presentaciones": ["ppt", "pptx"],
    "imagenes": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"],
    "videos": ["mp4", "mkv", "avi", "mov", "wmv", "flv"],
    "audios": ["mp3", "wav", "aac", "flac", "ogg"],
    "comprimidos": ["zip", "rar", "7z", "tar", "gz"],
    "ejecutables": ["exe", "msi", "bat", "sh", "apk"],
}

EXCLUSIONES_POR_DEFECTO = {
    ".git", "__pycache__", ".venv", ".vscode", ".idea", "node_modules",
}

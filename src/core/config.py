"""
Configuración centralizada para ADAM
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configuración principal de ADAM"""
    
    # Rutas base
    BASE_DIR: Path = Path(__file__).parent.parent.parent
    ADAM_DATA_DIR: Path = BASE_DIR / "adam_data"
    LOGS_DIR: Path = BASE_DIR / "logs"
    
    # Base de datos
    SQLITE_DB_PATH: Path = ADAM_DATA_DIR / "adam.db"
    CHROMA_DIR: Path = ADAM_DATA_DIR / "chroma"
    
    # Biblioteca de archivos
    LIBRARY_DIR: Path = ADAM_DATA_DIR / "library"
    DOCUMENTS_DIR: Path = LIBRARY_DIR / "documents"
    IMAGES_DIR: Path = LIBRARY_DIR / "images"
    
    # API Configuration
    API_HOST: str = "127.0.0.1"
    API_PORT: int = 8000
    API_TITLE: str = "ADAM - Artificial Digital Assistant for Memory"
    API_VERSION: str = "1.0.0"
    
    # Anthropic API
    ANTHROPIC_API_KEY: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
    LOG_FILE: Path = LOGS_DIR / "adam.log"
    
    # Memory & Intelligence
    MAX_MEMORY_CONTEXT: int = 10  # Número de conversaciones previas a considerar
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instancia global de configuración
settings = Settings()

def ensure_directories():
    """Asegura que todas las carpetas necesarias existan"""
    directories = [
        settings.ADAM_DATA_DIR,
        settings.LOGS_DIR,
        settings.CHROMA_DIR,
        settings.LIBRARY_DIR,
        settings.DOCUMENTS_DIR,
        settings.IMAGES_DIR,
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✓ Directorio creado/verificado: {directory}")

def get_database_url() -> str:
    """Retorna la URL de la base de datos SQLite"""
    return f"sqlite:///{settings.SQLITE_DB_PATH}"

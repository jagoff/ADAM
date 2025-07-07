"""
ADAM - Artificial Digital Assistant for Memory
Entry point principal de la aplicación
"""
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sys
from pathlib import Path

# Agregar el directorio src al path para imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.core.config import settings, ensure_directories
from src.api.chat import router as chat_router
from src.api.library import router as library_router

# Configurar logging
from loguru import logger
import logging

# Configurar loguru
logger.remove()  # Remover handler por defecto
logger.add(
    settings.LOG_FILE,
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL,
    rotation="10 MB",
    retention="30 days"
)
logger.add(
    sys.stdout,
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL
)

# Configurar logging estándar para FastAPI
logging.basicConfig(level=logging.INFO)
logging.getLogger("uvicorn").handlers = [logging.StreamHandler(sys.stdout)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para la aplicación"""
    # Startup
    logger.info("🚀 Iniciando ADAM - Artificial Digital Assistant for Memory")
    
    # Asegurar que todos los directorios existan
    ensure_directories()
    logger.info("✓ Directorios verificados")
    
    # TODO: Inicializar ChromaDB
    # TODO: Verificar conexión a Anthropic API
    
    logger.info("✅ ADAM está listo para recibir mensajes")
    
    yield
    
    # Shutdown
    logger.info("🛑 Cerrando ADAM")

# Crear aplicación FastAPI
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description="ADAM es un asistente de IA personal con memoria perfecta y coaching proactivo",
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(chat_router)
app.include_router(library_router)

@app.get("/")
async def root():
    """Endpoint raíz con información de ADAM"""
    return {
        "message": "ADAM - Artificial Digital Assistant for Memory",
        "version": settings.API_VERSION,
        "description": "Tu segundo cerebro digital con memoria perfecta",
        "endpoints": {
            "chat": "/chat/send",
            "history": "/chat/history/{session_id}",
            "search": "/chat/search",
            "summary": "/chat/summary",
            "entities": "/chat/entities",
            "health": "/chat/health",
            "library": "/library/files",
            "upload": "/library/upload",
            "docs": "/docs"
        },
        "features": [
            "Memoria perfecta - nunca olvida nada",
            "Organización orgánica - categorías emergentes",
            "Coaching proactivo - anticipa necesidades",
            "100% local - privacidad total"
        ]
    }

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Manejador global de excepciones"""
    logger.error(f"Error no manejado: {exc}")
    return HTTPException(
        status_code=500,
        detail="Error interno del servidor"
    )

if __name__ == "__main__":
    logger.info(f"🌐 Iniciando servidor en {settings.API_HOST}:{settings.API_PORT}")
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    )

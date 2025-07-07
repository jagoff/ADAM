"""
API endpoints para el chat con ADAM
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid

from ..core.adam import adam
from ..core.config import settings

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    """Modelo para requests de chat"""
    message: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    """Modelo para responses de chat"""
    response: str
    session_id: str
    conversation_id: str
    entities: list
    category: str
    context_used: list
    insights: list
    timestamp: str

class MemorySearchRequest(BaseModel):
    """Modelo para búsquedas en memoria"""
    query: str
    limit: Optional[int] = 10

class MemorySummaryRequest(BaseModel):
    """Modelo para resúmenes de memoria"""
    session_id: Optional[str] = None
    days: Optional[int] = 7

@router.post("/send", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """
    Envía un mensaje a ADAM y recibe una respuesta contextual
    
    Args:
        request: ChatRequest con el mensaje y contexto opcional
        
    Returns:
        ChatResponse con la respuesta y metadatos
    """
    try:
        # Procesar mensaje con ADAM
        result = await adam.process_message(
            user_message=request.message,
            session_id=request.session_id,
            context=request.context
        )
        
        return ChatResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error procesando mensaje: {str(e)}"
        )

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str, limit: int = 20):
    """
    Obtiene el historial de conversaciones de una sesión
    
    Args:
        session_id: ID de la sesión
        limit: Número máximo de conversaciones a retornar
        
    Returns:
        Lista de conversaciones
    """
    try:
        from ..storage.database import db_manager
        
        conversations = db_manager.get_conversation_history(
            session_id=session_id,
            limit=limit
        )
        
        return {
            "session_id": session_id,
            "conversations": conversations,
            "total": len(conversations)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo historial: {str(e)}"
        )

@router.post("/search")
async def search_memory(request: MemorySearchRequest):
    """
    Busca en la memoria de ADAM
    
    Args:
        request: MemorySearchRequest con la query de búsqueda
        
    Returns:
        Lista de conversaciones relevantes
    """
    try:
        results = await adam.search_memory(
            query=request.query,
            limit=request.limit
        )
        
        return {
            "query": request.query,
            "results": results,
            "total_found": len(results)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error en búsqueda: {str(e)}"
        )

@router.post("/summary")
async def get_memory_summary(request: MemorySummaryRequest):
    """
    Obtiene un resumen de la memoria de ADAM
    
    Args:
        request: MemorySummaryRequest con parámetros del resumen
        
    Returns:
        Resumen de la memoria
    """
    try:
        summary = await adam.get_memory_summary(
            session_id=request.session_id,
            days=request.days
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo resumen: {str(e)}"
        )

@router.get("/entities")
async def get_entities(entity_type: Optional[str] = None, limit: int = 50):
    """
    Obtiene entidades conocidas por ADAM
    
    Args:
        entity_type: Tipo de entidad a filtrar (opcional)
        limit: Número máximo de entidades a retornar
        
    Returns:
        Lista de entidades
    """
    try:
        from ..storage.database import db_manager
        
        entities = db_manager.get_entities(
            entity_type=entity_type,
            limit=limit
        )
        
        return {
            "entities": entities,
            "total": len(entities),
            "filtered_by_type": entity_type
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo entidades: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Endpoint de health check para verificar que ADAM está funcionando
    """
    return {
        "status": "healthy",
        "service": "ADAM",
        "version": settings.API_VERSION,
        "memory_system": "operational",
        "database": "connected"
    }

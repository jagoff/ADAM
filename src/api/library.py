"""
API endpoints para gestión de biblioteca de archivos
"""
from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict
import os

from ..storage.local_storage import LocalStorage
from ..intelligence.categorizer import ContentCategorizer

router = APIRouter(prefix="/library", tags=["library"])

# Instancias
local_storage = LocalStorage()
categorizer = ContentCategorizer()

class FileUploadResponse(BaseModel):
    """Modelo para respuesta de upload de archivo"""
    file_id: str
    original_name: str
    stored_path: str
    category: str
    file_size: int
    metadata: Dict

class FileListResponse(BaseModel):
    """Modelo para respuesta de lista de archivos"""
    files: List[Dict]
    total: int
    category: Optional[str]

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    category: Optional[str] = None,
    metadata: Optional[Dict] = None
):
    """
    Sube un archivo a la biblioteca de ADAM
    
    Args:
        file: Archivo a subir
        category: Categoría del archivo (opcional)
        metadata: Metadatos adicionales (opcional)
        
    Returns:
        Información del archivo almacenado
    """
    try:
        # Guardar archivo temporalmente
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Categorizar automáticamente si no se especifica
        if not category:
            # TODO: Implementar categorización basada en contenido del archivo
            category = "general"
        
        # Almacenar en biblioteca local
        file_info = await local_storage.store_file(
            file_path=temp_path,
            original_name=file.filename,
            category=category,
            metadata=metadata
        )
        
        # Limpiar archivo temporal
        os.remove(temp_path)
        
        return FileUploadResponse(**file_info)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error subiendo archivo: {str(e)}"
        )

@router.get("/files", response_model=FileListResponse)
async def list_files(
    category: Optional[str] = None,
    limit: int = 50
):
    """
    Lista archivos en la biblioteca
    
    Args:
        category: Categoría a filtrar (opcional)
        limit: Número máximo de archivos
        
    Returns:
        Lista de archivos
    """
    try:
        files = await local_storage.list_files(
            category=category,
            limit=limit
        )
        
        return FileListResponse(
            files=files,
            total=len(files),
            category=category
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error listando archivos: {str(e)}"
        )

@router.get("/files/{file_id}")
async def get_file_info(file_id: str):
    """
    Obtiene información de un archivo específico
    
    Args:
        file_id: ID del archivo
        
    Returns:
        Información del archivo
    """
    try:
        # TODO: Implementar búsqueda por ID
        # Por ahora, buscar por nombre
        files = await local_storage.list_files(limit=1000)
        
        for file_info in files:
            if file_info.get("name") == file_id:
                return file_info
        
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo información del archivo: {str(e)}"
        )

@router.delete("/files/{file_id}")
async def delete_file(file_id: str):
    """
    Elimina un archivo de la biblioteca
    
    Args:
        file_id: ID del archivo a eliminar
        
    Returns:
        Confirmación de eliminación
    """
    try:
        # TODO: Implementar eliminación por ID
        # Por ahora, buscar por nombre
        files = await local_storage.list_files(limit=1000)
        
        for file_info in files:
            if file_info.get("name") == file_id:
                success = await local_storage.delete_file(file_info["path"])
                if success:
                    return {"message": "Archivo eliminado correctamente"}
                else:
                    raise HTTPException(
                        status_code=500,
                        detail="Error eliminando archivo"
                    )
        
        raise HTTPException(
            status_code=404,
            detail="Archivo no encontrado"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error eliminando archivo: {str(e)}"
        )

@router.get("/categories")
async def get_categories():
    """
    Obtiene las categorías disponibles en la biblioteca
    
    Returns:
        Lista de categorías
    """
    try:
        hierarchy = categorizer.get_category_hierarchy()
        
        return {
            "categories": hierarchy,
            "total": len(hierarchy)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo categorías: {str(e)}"
        )

@router.get("/stats")
async def get_library_stats():
    """
    Obtiene estadísticas de la biblioteca
    
    Returns:
        Estadísticas del almacenamiento
    """
    try:
        stats = local_storage.get_storage_stats()
        
        return {
            "library_stats": stats,
            "categories": categorizer.get_category_hierarchy()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error obteniendo estadísticas: {str(e)}"
        )

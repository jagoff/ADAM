"""
Sistema de almacenamiento local para ADAM
Gestión de archivos y organización automática
"""
import os
import hashlib
import shutil
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

from ..core.config import settings

class LocalStorage:
    """Sistema de almacenamiento local de archivos para ADAM"""
    
    def __init__(self):
        """Inicializa el sistema de almacenamiento"""
        self.base_dir = settings.LIBRARY_DIR
        self.documents_dir = settings.DOCUMENTS_DIR
        self.images_dir = settings.IMAGES_DIR
    
    async def store_file(
        self,
        file_path: str,
        original_name: str,
        category: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Almacena un archivo en la biblioteca local
        
        Args:
            file_path: Ruta del archivo original
            original_name: Nombre original del archivo
            category: Categoría del archivo
            metadata: Metadatos adicionales
            
        Returns:
            Diccionario con información del archivo almacenado
        """
        # Crear estructura de directorios
        category_path = self._create_category_path(category)
        
        # Generar nombre único para el archivo
        file_hash = self._generate_file_hash(file_path)
        file_extension = Path(original_name).suffix
        stored_name = f"{file_hash}{file_extension}"
        
        # Ruta final del archivo
        final_path = category_path / stored_name
        
        # Copiar archivo
        shutil.copy2(file_path, final_path)
        
        # Preparar metadatos
        file_info = {
            "original_name": original_name,
            "stored_path": str(final_path),
            "category": category,
            "file_hash": file_hash,
            "file_size": os.path.getsize(final_path),
            "stored_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        return file_info
    
    def _create_category_path(self, category: str) -> Path:
        """
        Crea la ruta de categoría si no existe
        
        Args:
            category: Categoría del archivo
            
        Returns:
            Path de la categoría
        """
        # Determinar directorio base según tipo de archivo
        if category in ["documents", "pdf", "text"]:
            base_category_dir = self.documents_dir
        elif category in ["images", "photos", "screenshots"]:
            base_category_dir = self.images_dir
        else:
            base_category_dir = self.base_dir
        
        # Crear ruta de categoría
        category_path = base_category_dir / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        return category_path
    
    def _generate_file_hash(self, file_path: str) -> str:
        """
        Genera hash único para un archivo
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Hash del archivo
        """
        hash_md5 = hashlib.md5()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        
        return hash_md5.hexdigest()
    
    async def get_file_info(self, file_path: str) -> Optional[Dict]:
        """
        Obtiene información de un archivo almacenado
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Información del archivo o None si no existe
        """
        path = Path(file_path)
        
        if not path.exists():
            return None
        
        return {
            "path": str(path),
            "name": path.name,
            "size": path.stat().st_size,
            "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            "category": self._infer_category_from_path(path)
        }
    
    def _infer_category_from_path(self, file_path: Path) -> str:
        """
        Infiere la categoría basada en la ruta del archivo
        
        Args:
            file_path: Path del archivo
            
        Returns:
            Categoría inferida
        """
        # Buscar categoría en la ruta
        for part in file_path.parts:
            if part in ["documents", "images", "work", "personal", "family"]:
                return part
        
        # Inferir por extensión
        extension = file_path.suffix.lower()
        if extension in [".pdf", ".doc", ".docx", ".txt"]:
            return "documents"
        elif extension in [".jpg", ".jpeg", ".png", ".gif"]:
            return "images"
        
        return "general"
    
    async def list_files(
        self,
        category: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Lista archivos almacenados
        
        Args:
            category: Categoría a filtrar (opcional)
            limit: Número máximo de archivos
            
        Returns:
            Lista de archivos
        """
        files = []
        
        if category:
            # Buscar en categoría específica
            category_path = self.base_dir / category
            if category_path.exists():
                files.extend(self._scan_directory(category_path, limit))
        else:
            # Buscar en todos los directorios
            for root, dirs, filenames in os.walk(self.base_dir):
                for filename in filenames:
                    if len(files) >= limit:
                        break
                    
                    file_path = Path(root) / filename
                    file_info = await self.get_file_info(str(file_path))
                    if file_info:
                        files.append(file_info)
        
        return files[:limit]
    
    def _scan_directory(self, directory: Path, limit: int) -> List[Dict]:
        """
        Escanea un directorio en busca de archivos
        
        Args:
            directory: Directorio a escanear
            limit: Número máximo de archivos
            
        Returns:
            Lista de archivos encontrados
        """
        files = []
        
        for file_path in directory.iterdir():
            if len(files) >= limit:
                break
            
            if file_path.is_file():
                file_info = {
                    "path": str(file_path),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                    "category": self._infer_category_from_path(file_path)
                }
                files.append(file_info)
        
        return files
    
    async def delete_file(self, file_path: str) -> bool:
        """
        Elimina un archivo almacenado
        
        Args:
            file_path: Ruta del archivo a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
            return False
        except Exception:
            return False
    
    def get_storage_stats(self) -> Dict:
        """
        Obtiene estadísticas del almacenamiento
        
        Returns:
            Diccionario con estadísticas
        """
        total_size = 0
        file_count = 0
        category_stats = {}
        
        for root, dirs, filenames in os.walk(self.base_dir):
            for filename in filenames:
                file_path = Path(root) / filename
                if file_path.exists():
                    file_size = file_path.stat().st_size
                    total_size += file_size
                    file_count += 1
                    
                    category = self._infer_category_from_path(file_path)
                    if category not in category_stats:
                        category_stats[category] = {"count": 0, "size": 0}
                    category_stats[category]["count"] += 1
                    category_stats[category]["size"] += file_size
        
        return {
            "total_files": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "categories": category_stats
        }

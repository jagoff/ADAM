"""
Sistema de memoria para ADAM
Gestión de memoria contextual y búsqueda semántica
"""
from typing import List, Dict, Optional
from ..storage.database import db_manager

class MemorySystem:
    """Sistema de memoria contextual de ADAM"""
    
    def __init__(self):
        """Inicializa el sistema de memoria"""
        self.max_context = 10  # Número de conversaciones previas a considerar
    
    async def get_relevant_context(
        self,
        user_message: str,
        entities: List[Dict],
        session_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Obtiene contexto relevante basado en el mensaje y entidades
        
        Args:
            user_message: Mensaje actual del usuario
            entities: Entidades detectadas en el mensaje
            session_id: ID de la sesión actual
            
        Returns:
            Lista de conversaciones relevantes
        """
        # TODO: Implementar búsqueda semántica con ChromaDB
        # Por ahora, búsqueda básica por entidades
        
        relevant_context = []
        
        # Buscar conversaciones que mencionen las mismas entidades
        for entity in entities:
            entity_name = entity.get("name", "")
            if entity_name:
                # Buscar en conversaciones recientes
                conversations = db_manager.get_conversation_history(limit=50)
                
                for conv in conversations:
                    conv_entities = conv.get("entities", [])
                    for conv_entity in conv_entities:
                        if conv_entity.get("name", "").lower() == entity_name.lower():
                            relevant_context.append(conv)
                            break
        
        # Si no hay contexto por entidades, buscar por palabras clave
        if not relevant_context:
            relevant_context = self._search_by_keywords(user_message)
        
        # Limitar el contexto
        return relevant_context[:self.max_context]
    
    def _search_by_keywords(self, user_message: str) -> List[Dict]:
        """
        Búsqueda básica por palabras clave
        """
        conversations = db_manager.get_conversation_history(limit=20)
        relevant = []
        
        # Extraer palabras clave del mensaje
        keywords = [word.lower() for word in user_message.split() if len(word) > 3]
        
        for conv in conversations:
            message_lower = conv.get("user_message", "").lower()
            if any(keyword in message_lower for keyword in keywords):
                relevant.append(conv)
        
        return relevant
    
    async def store_memory(
        self,
        content: str,
        entities: List[Dict],
        metadata: Optional[Dict] = None
    ) -> str:
        """
        Almacena contenido en la memoria
        
        Args:
            content: Contenido a almacenar
            entities: Entidades detectadas
            metadata: Metadatos adicionales
            
        Returns:
            ID del elemento almacenado
        """
        # TODO: Integrar con ChromaDB para almacenamiento vectorial
        # Por ahora, solo se almacena en SQLite a través de save_conversation
        
        return "memory_id_placeholder"
    
    async def search_memory(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Busca en la memoria usando búsqueda semántica
        
        Args:
            query: Query de búsqueda
            limit: Número máximo de resultados
            
        Returns:
            Lista de elementos relevantes
        """
        # TODO: Implementar búsqueda semántica con ChromaDB
        # Por ahora, búsqueda básica en SQLite
        
        conversations = db_manager.get_conversation_history(limit=limit)
        relevant = self._search_by_keywords(query)
        
        return relevant[:limit]
    
    def get_memory_stats(self) -> Dict:
        """
        Obtiene estadísticas de la memoria
        
        Returns:
            Diccionario con estadísticas
        """
        conversations = db_manager.get_conversation_history(limit=1000)
        entities = db_manager.get_entities(limit=1000)
        
        return {
            "total_conversations": len(conversations),
            "total_entities": len(entities),
            "memory_size_mb": 0,  # TODO: Calcular tamaño real
            "last_updated": conversations[0].get("timestamp") if conversations else None
        }

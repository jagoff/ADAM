"""
Clase principal de ADAM - Artificial Digital Assistant for Memory
Orquesta todos los componentes del sistema
"""
import uuid
from typing import List, Dict, Optional, Any
from datetime import datetime

from .config import settings
from ..storage.database import db_manager
from ..memory.memory_system import MemorySystem
from ..intelligence.entity_recognition import EntityRecognizer
from ..intelligence.categorizer import ContentCategorizer
from ..intelligence.coach import Coach

class ADAM:
    """
    Clase principal de ADAM que coordina todos los sistemas
    """
    
    def __init__(self):
        """Inicializa ADAM con todos sus componentes"""
        self.memory_system = MemorySystem()
        self.entity_recognizer = EntityRecognizer()
        self.categorizer = ContentCategorizer()
        self.coach = Coach()
        
        # Configuración de personalidad
        self.personality = {
            "name": "ADAM",
            "tone": "directo pero empático",
            "style": "proactivo y contextual",
            "memory_focus": "recuerda todo, conecta patrones"
        }
    
    async def process_message(
        self,
        user_message: str,
        session_id: Optional[str] = None,
        context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Procesa un mensaje del usuario y genera una respuesta contextual
        
        Args:
            user_message: Mensaje del usuario
            session_id: ID de la sesión (opcional)
            context: Contexto adicional (opcional)
            
        Returns:
            Dict con la respuesta y metadatos
        """
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 1. Extraer entidades del mensaje
        entities = await self.entity_recognizer.extract_entities(user_message)
        
        # 2. Categorizar el contenido
        category = await self.categorizer.categorize_content(user_message, entities)
        
        # 3. Buscar contexto relevante en memoria
        relevant_context = await self.memory_system.get_relevant_context(
            user_message, entities, session_id
        )
        
        # 4. Generar respuesta contextual
        response = await self._generate_contextual_response(
            user_message, entities, relevant_context, category
        )
        
        # 5. Guardar en memoria
        conversation_id = db_manager.save_conversation(
            session_id=session_id,
            user_message=user_message,
            adam_response=response["text"],
            entities=entities,
            chroma_id=response.get("chroma_id")
        )
        
        # 6. Actualizar entidades y relaciones
        await self._update_entities_and_relationships(entities, user_message)
        
        # 7. Generar insights y sugerencias proactivas
        insights = await self.coach.generate_insights(
            user_message, entities, relevant_context
        )
        
        return {
            "response": response["text"],
            "session_id": session_id,
            "conversation_id": conversation_id,
            "entities": entities,
            "category": category,
            "context_used": relevant_context,
            "insights": insights,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _generate_contextual_response(
        self,
        user_message: str,
        entities: List[Dict],
        relevant_context: List[Dict],
        category: str
    ) -> Dict[str, str]:
        """
        Genera una respuesta contextual basada en el mensaje y la memoria
        """
        # Construir prompt contextual
        context_summary = self._build_context_summary(relevant_context, entities)
        
        # TODO: Integrar con Anthropic API cuando esté configurada
        # Por ahora, respuesta básica contextual
        response_text = self._generate_basic_response(
            user_message, entities, context_summary, category
        )
        
        return {
            "text": response_text,
            "chroma_id": None  # TODO: Integrar con ChromaDB
        }
    
    def _build_context_summary(
        self,
        relevant_context: List[Dict],
        current_entities: List[Dict]
    ) -> str:
        """Construye un resumen del contexto relevante"""
        if not relevant_context:
            return ""
        
        summary_parts = []
        
        # Agrupar por entidades mencionadas
        entity_contexts = {}
        for context in relevant_context:
            for entity in context.get("entities", []):
                entity_name = entity.get("name", "")
                if entity_name not in entity_contexts:
                    entity_contexts[entity_name] = []
                entity_contexts[entity_name].append(context)
        
        # Construir resumen por entidad
        for entity_name, contexts in entity_contexts.items():
            if entity_name:
                summary_parts.append(f"Contexto sobre {entity_name}:")
                for ctx in contexts[:3]:  # Máximo 3 contextos por entidad
                    summary_parts.append(f"- {ctx.get('user_message', '')[:100]}...")
        
        return "\n".join(summary_parts)
    
    def _generate_basic_response(
        self,
        user_message: str,
        entities: List[Dict],
        context_summary: str,
        category: str
    ) -> str:
        """
        Genera una respuesta básica contextual (placeholder hasta integrar LLM)
        """
        # Detectar tipo de mensaje
        message_lower = user_message.lower()
        
        if any(word in message_lower for word in ["hola", "buenos días", "buenas"]):
            return self._generate_greeting_response(entities, context_summary)
        
        elif any(word in message_lower for word in ["recordar", "recordás", "recuerdas"]):
            return self._generate_memory_response(entities, context_summary)
        
        elif any(word in message_lower for word in ["guardar", "save", "almacenar"]):
            return self._generate_storage_response(user_message, category)
        
        else:
            return self._generate_general_response(user_message, entities, context_summary)
    
    def _generate_greeting_response(
        self,
        entities: List[Dict],
        context_summary: str
    ) -> str:
        """Genera respuesta a saludos con contexto"""
        if context_summary:
            return f"¡Hola! Veo que has estado trabajando en temas relacionados. {context_summary[:200]}..."
        else:
            return "¡Hola! Soy ADAM, tu asistente de memoria. ¿En qué puedo ayudarte hoy?"
    
    def _generate_memory_response(
        self,
        entities: List[Dict],
        context_summary: str
    ) -> str:
        """Genera respuesta sobre memoria"""
        if entities and context_summary:
            entity_names = [e.get("name", "") for e in entities if e.get("name")]
            if entity_names:
                return f"Sí, recuerdo sobre {', '.join(entity_names)}. {context_summary[:300]}..."
        
        return "Estoy aquí para recordar todo lo que me compartas. ¿Qué te gustaría que recuerde?"
    
    def _generate_storage_response(
        self,
        user_message: str,
        category: str
    ) -> str:
        """Genera respuesta para almacenamiento"""
        return f"Perfecto, he guardado esa información en la categoría '{category}'. ¿Hay algo más que quieras que recuerde?"
    
    def _generate_general_response(
        self,
        user_message: str,
        entities: List[Dict],
        context_summary: str
    ) -> str:
        """Genera respuesta general contextual"""
        if context_summary:
            return f"Entiendo. {context_summary[:200]}... ¿Hay algo específico sobre esto que te gustaría que recuerde o analice?"
        else:
            return "Interesante. Estoy guardando esta información para futuras referencias. ¿Hay algo más que quieras compartir?"
    
    async def _update_entities_and_relationships(
        self,
        entities: List[Dict],
        user_message: str
    ):
        """Actualiza entidades y relaciones en la base de datos"""
        for entity in entities:
            entity_id = db_manager.save_entity(
                name=entity.get("name", ""),
                entity_type=entity.get("type", "unknown"),
                metadata=entity.get("metadata", {})
            )
            
            # Crear relaciones entre entidades mencionadas juntas
            for other_entity in entities:
                if other_entity != entity:
                    db_manager.save_relationship(
                        entity1_id=entity_id,
                        entity2_id=other_entity.get("id", ""),
                        relationship_type="mentioned_together",
                        context=user_message[:200]
                    )
    
    async def get_memory_summary(
        self,
        session_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Genera un resumen de la memoria reciente
        """
        conversations = db_manager.get_conversation_history(session_id, limit=50)
        entities = db_manager.get_entities(limit=20)
        
        return {
            "recent_conversations": len(conversations),
            "top_entities": entities[:10],
            "categories_found": self._extract_categories(conversations),
            "summary": f"En los últimos {days} días, hemos tenido {len(conversations)} conversaciones sobre {len(entities)} entidades diferentes."
        }
    
    def _extract_categories(self, conversations: List[Dict]) -> List[str]:
        """Extrae categorías únicas de las conversaciones"""
        categories = set()
        for conv in conversations:
            # TODO: Implementar extracción de categorías más sofisticada
            pass
        return list(categories)
    
    async def search_memory(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Busca en la memoria usando búsqueda semántica
        """
        # TODO: Integrar con ChromaDB para búsqueda semántica
        # Por ahora, búsqueda básica en SQLite
        conversations = db_manager.get_conversation_history(limit=limit)
        
        # Filtrado básico por palabras clave
        relevant_conversations = []
        query_words = query.lower().split()
        
        for conv in conversations:
            message_lower = conv.get("user_message", "").lower()
            if any(word in message_lower for word in query_words):
                relevant_conversations.append(conv)
        
        return relevant_conversations[:limit]

# Instancia global de ADAM
adam = ADAM()

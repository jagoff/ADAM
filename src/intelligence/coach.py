"""
Sistema de coaching inteligente para ADAM
Genera insights y sugerencias proactivas
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class Coach:
    """Sistema de coaching proactivo de ADAM"""
    
    def __init__(self):
        """Inicializa el sistema de coaching"""
        self.insight_patterns = {
            "productivity": {
                "keywords": ["productivo", "productivity", "eficiente", "efficient"],
                "weight": 1.0
            },
            "follow_up": {
                "keywords": ["pendiente", "pending", "seguimiento", "follow up"],
                "weight": 1.0
            },
            "reminder": {
                "keywords": ["recordar", "remind", "olvidar", "forget"],
                "weight": 1.0
            },
            "pattern": {
                "keywords": ["patrón", "pattern", "tendencia", "trend"],
                "weight": 1.0
            }
        }
    
    async def generate_insights(
        self,
        user_message: str,
        entities: List[Dict],
        relevant_context: List[Dict]
    ) -> List[Dict]:
        """
        Genera insights y sugerencias proactivas
        
        Args:
            user_message: Mensaje actual del usuario
            entities: Entidades detectadas
            relevant_context: Contexto relevante de conversaciones previas
            
        Returns:
            Lista de insights y sugerencias
        """
        insights = []
        
        # Analizar el mensaje para detectar oportunidades de coaching
        message_insights = self._analyze_message_for_insights(
            user_message, entities, relevant_context
        )
        insights.extend(message_insights)
        
        # Generar recordatorios basados en entidades
        reminder_insights = self._generate_reminders(entities, relevant_context)
        insights.extend(reminder_insights)
        
        # Detectar patrones de comportamiento
        pattern_insights = self._detect_patterns(user_message, relevant_context)
        insights.extend(pattern_insights)
        
        # Generar sugerencias proactivas
        proactive_suggestions = self._generate_proactive_suggestions(
            user_message, entities, relevant_context
        )
        insights.extend(proactive_suggestions)
        
        return insights[:5]  # Limitar a 5 insights máximo
    
    def _analyze_message_for_insights(
        self,
        user_message: str,
        entities: List[Dict],
        relevant_context: List[Dict]
    ) -> List[Dict]:
        """
        Analiza el mensaje para detectar oportunidades de coaching
        """
        insights = []
        message_lower = user_message.lower()
        
        # Detectar si es una reunión o evento
        if any(word in message_lower for word in ["reunión", "meeting", "call"]):
            insights.append({
                "type": "follow_up",
                "priority": "medium",
                "message": "¿Te gustaría que programe un recordatorio para hacer seguimiento después de esta reunión?",
                "suggestion": "Agregar recordatorio de seguimiento"
            })
        
        # Detectar si menciona deadlines
        if any(word in message_lower for word in ["deadline", "fecha límite", "entrega"]):
            insights.append({
                "type": "reminder",
                "priority": "high",
                "message": "Veo que mencionas un deadline. ¿Quieres que te ayude a organizar las tareas pendientes?",
                "suggestion": "Crear lista de tareas para el deadline"
            })
        
        # Detectar si es información personal importante
        if any(word in message_lower for word in ["cumpleaños", "birthday", "aniversario"]):
            insights.append({
                "type": "reminder",
                "priority": "medium",
                "message": "Información personal importante detectada. ¿Quieres que programe recordatorios anuales?",
                "suggestion": "Configurar recordatorio anual"
            })
        
        return insights
    
    def _generate_reminders(
        self,
        entities: List[Dict],
        relevant_context: List[Dict]
    ) -> List[Dict]:
        """
        Genera recordatorios basados en entidades y contexto
        """
        reminders = []
        
        for entity in entities:
            entity_type = entity.get("type", "")
            entity_name = entity.get("name", "")
            
            # Recordatorios para personas
            if entity_type == "person":
                # Buscar conversaciones previas sobre esta persona
                person_context = self._get_person_context(entity_name, relevant_context)
                
                if person_context:
                    reminders.append({
                        "type": "follow_up",
                        "priority": "medium",
                        "message": f"¿Cómo estuvo tu última interacción con {entity_name}?",
                        "suggestion": f"Revisar conversaciones previas con {entity_name}",
                        "entity": entity_name
                    })
            
            # Recordatorios para proyectos
            elif entity_type == "project":
                reminders.append({
                    "type": "follow_up",
                    "priority": "medium",
                    "message": f"¿Hay actualizaciones sobre el proyecto {entity_name}?",
                    "suggestion": f"Actualizar estado del proyecto {entity_name}",
                    "entity": entity_name
                })
        
        return reminders
    
    def _get_person_context(
        self,
        person_name: str,
        relevant_context: List[Dict]
    ) -> List[Dict]:
        """
        Obtiene contexto específico sobre una persona
        """
        person_context = []
        
        for context in relevant_context:
            context_entities = context.get("entities", [])
            for entity in context_entities:
                if entity.get("name", "").lower() == person_name.lower():
                    person_context.append(context)
                    break
        
        return person_context
    
    def _detect_patterns(
        self,
        user_message: str,
        relevant_context: List[Dict]
    ) -> List[Dict]:
        """
        Detecta patrones de comportamiento
        """
        patterns = []
        
        # Analizar frecuencia de temas
        topic_frequency = self._analyze_topic_frequency(relevant_context)
        
        # Detectar temas recurrentes
        for topic, frequency in topic_frequency.items():
            if frequency > 3:  # Más de 3 menciones
                patterns.append({
                    "type": "pattern",
                    "priority": "low",
                    "message": f"Veo que {topic} es un tema recurrente en nuestras conversaciones.",
                    "suggestion": f"¿Te gustaría que profundice en {topic}?",
                    "pattern": topic,
                    "frequency": frequency
                })
        
        # Detectar horarios de actividad
        time_patterns = self._analyze_time_patterns(relevant_context)
        if time_patterns:
            patterns.append({
                "type": "pattern",
                "priority": "low",
                "message": f"Detecto que eres más activo en {time_patterns}",
                "suggestion": "¿Quieres que programe recordatorios para esos horarios?",
                "pattern": "time_activity"
            })
        
        return patterns
    
    def _analyze_topic_frequency(self, relevant_context: List[Dict]) -> Dict[str, int]:
        """
        Analiza la frecuencia de temas en el contexto
        """
        topic_frequency = {}
        
        for context in relevant_context:
            message = context.get("user_message", "").lower()
            
            # Categorías de temas
            topics = {
                "trabajo": ["trabajo", "work", "proyecto", "project"],
                "personal": ["familia", "family", "amigos", "friends"],
                "salud": ["ejercicio", "exercise", "salud", "health"],
                "finanzas": ["dinero", "money", "presupuesto", "budget"]
            }
            
            for topic, keywords in topics.items():
                if any(keyword in message for keyword in keywords):
                    topic_frequency[topic] = topic_frequency.get(topic, 0) + 1
        
        return topic_frequency
    
    def _analyze_time_patterns(self, relevant_context: List[Dict]) -> Optional[str]:
        """
        Analiza patrones de tiempo en las conversaciones
        """
        # TODO: Implementar análisis de timestamps
        # Por ahora, retorna None
        return None
    
    def _generate_proactive_suggestions(
        self,
        user_message: str,
        entities: List[Dict],
        relevant_context: List[Dict]
    ) -> List[Dict]:
        """
        Genera sugerencias proactivas basadas en el contexto
        """
        suggestions = []
        
        # Sugerir organización si hay muchas entidades
        if len(entities) > 3:
            suggestions.append({
                "type": "organization",
                "priority": "medium",
                "message": "Veo que mencionas varios elementos. ¿Te gustaría que organice esta información?",
                "suggestion": "Crear categorías automáticas"
            })
        
        # Sugerir búsqueda si hay contexto relevante
        if relevant_context:
            suggestions.append({
                "type": "search",
                "priority": "low",
                "message": "Tengo información relacionada. ¿Quieres que busque más contexto?",
                "suggestion": "Buscar información relacionada"
            })
        
        # Sugerir recordatorios para fechas
        date_entities = [e for e in entities if e.get("type") == "date"]
        if date_entities:
            suggestions.append({
                "type": "reminder",
                "priority": "medium",
                "message": "Detecté fechas importantes. ¿Quieres que configure recordatorios?",
                "suggestion": "Configurar recordatorios de fechas"
            })
        
        return suggestions
    
    async def generate_daily_brief(self, session_id: Optional[str] = None) -> Dict:
        """
        Genera un brief diario con resumen y sugerencias
        
        Args:
            session_id: ID de la sesión (opcional)
            
        Returns:
            Diccionario con el brief diario
        """
        # TODO: Implementar brief diario completo
        # Por ahora, estructura básica
        
        brief = {
            "date": datetime.now().isoformat(),
            "summary": "Resumen del día",
            "pending_items": [],
            "suggestions": [],
            "reminders": []
        }
        
        return brief
    
    def get_coaching_stats(self) -> Dict:
        """
        Obtiene estadísticas del sistema de coaching
        
        Returns:
            Diccionario con estadísticas
        """
        return {
            "insights_generated": 0,  # TODO: Implementar contador
            "suggestions_accepted": 0,  # TODO: Implementar tracking
            "patterns_detected": 0,  # TODO: Implementar contador
            "reminders_active": 0  # TODO: Implementar contador
        }

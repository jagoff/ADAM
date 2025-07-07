"""
Sistema de categorización automática para ADAM
Clasifica contenido en categorías emergentes
"""
from typing import List, Dict, Optional

class ContentCategorizer:
    """Categorizador automático de contenido para ADAM"""
    
    def __init__(self):
        """Inicializa el categorizador"""
        # Categorías base y sus palabras clave
        self.categories = {
            "work": {
                "keywords": [
                    "reunión", "meeting", "proyecto", "project", "trabajo", "work",
                    "deadline", "fecha límite", "presentación", "demo", "código",
                    "desarrollo", "development", "api", "database", "frontend",
                    "backend", "devops", "finops", "presupuesto", "budget"
                ],
                "weight": 1.0
            },
            "personal": {
                "keywords": [
                    "familia", "family", "amigos", "friends", "cumpleaños", "birthday",
                    "vacaciones", "vacation", "casa", "home", "hobby", "pasatiempo"
                ],
                "weight": 1.0
            },
            "health": {
                "keywords": [
                    "ejercicio", "exercise", "gimnasio", "gym", "médico", "doctor",
                    "salud", "health", "dieta", "diet", "bienestar", "wellness"
                ],
                "weight": 1.0
            },
            "learning": {
                "keywords": [
                    "estudiar", "study", "curso", "course", "libro", "book",
                    "aprender", "learn", "investigación", "research", "tutorial"
                ],
                "weight": 1.0
            },
            "finance": {
                "keywords": [
                    "dinero", "money", "inversión", "investment", "ahorro", "saving",
                    "gasto", "expense", "presupuesto", "budget", "finanzas", "finance"
                ],
                "weight": 1.0
            },
            "links": {
                "keywords": [
                    "http", "www", "link", "url", "sitio", "website", "artículo",
                    "article", "recurso", "resource", "documentación", "docs"
                ],
                "weight": 1.0
            },
            "tasks": {
                "keywords": [
                    "tarea", "task", "hacer", "do", "completar", "complete",
                    "pendiente", "pending", "lista", "list", "checklist"
                ],
                "weight": 1.0
            },
            "events": {
                "keywords": [
                    "evento", "event", "conferencia", "conference", "seminario",
                    "seminar", "workshop", "taller", "cita", "appointment"
                ],
                "weight": 1.0
            }
        }
        
        # Subcategorías específicas
        self.subcategories = {
            "work": {
                "development": ["código", "programming", "desarrollo", "development"],
                "meetings": ["reunión", "meeting", "call", "llamada"],
                "projects": ["proyecto", "project", "finops", "devops"],
                "planning": ["planificación", "planning", "roadmap", "estrategia"]
            },
            "personal": {
                "family": ["familia", "family", "hijos", "children"],
                "friends": ["amigos", "friends", "social", "sociales"],
                "hobbies": ["hobby", "pasatiempo", "interés", "interest"]
            }
        }
    
    async def categorize_content(
        self,
        text: str,
        entities: List[Dict]
    ) -> str:
        """
        Categoriza el contenido basado en el texto y entidades
        
        Args:
            text: Texto a categorizar
            entities: Entidades detectadas en el texto
            
        Returns:
            Categoría principal del contenido
        """
        text_lower = text.lower()
        scores = {}
        
        # Calcular scores por categoría
        for category, config in self.categories.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in text_lower:
                    score += config["weight"]
            
            # Bonus por entidades específicas
            entity_bonus = self._calculate_entity_bonus(category, entities)
            score += entity_bonus
            
            scores[category] = score
        
        # Determinar categoría principal
        if not scores or max(scores.values()) == 0:
            return "general"
        
        primary_category = max(scores, key=scores.get)
        return primary_category
    
    def _calculate_entity_bonus(self, category: str, entities: List[Dict]) -> float:
        """
        Calcula bonus de score basado en entidades detectadas
        
        Args:
            category: Categoría a evaluar
            entities: Lista de entidades
            
        Returns:
            Bonus de score
        """
        bonus = 0.0
        
        for entity in entities:
            entity_type = entity.get("type", "")
            entity_name = entity.get("name", "").lower()
            
            # Bonus por tipo de entidad
            if category == "work" and entity_type in ["project", "company"]:
                bonus += 0.5
            elif category == "personal" and entity_type == "person":
                bonus += 0.3
            elif category == "events" and entity_type == "date":
                bonus += 0.2
            
            # Bonus por nombres específicos
            if category == "work" and entity_name in ["finops", "devops", "api"]:
                bonus += 0.3
            elif category == "personal" and entity_name in ["maría", "marco", "juan"]:
                bonus += 0.2
        
        return bonus
    
    async def get_subcategory(
        self,
        text: str,
        primary_category: str
    ) -> Optional[str]:
        """
        Obtiene la subcategoría específica
        
        Args:
            text: Texto a analizar
            primary_category: Categoría principal
            
        Returns:
            Subcategoría específica
        """
        if primary_category not in self.subcategories:
            return None
        
        text_lower = text.lower()
        subcategory_scores = {}
        
        for subcategory, keywords in self.subcategories[primary_category].items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            subcategory_scores[subcategory] = score
        
        if not subcategory_scores or max(subcategory_scores.values()) == 0:
            return None
        
        return max(subcategory_scores, key=subcategory_scores.get)
    
    def suggest_category_path(
        self,
        primary_category: str,
        subcategory: Optional[str] = None,
        entities: List[Dict] = None
    ) -> str:
        """
        Sugiere una ruta de categoría para almacenamiento
        
        Args:
            primary_category: Categoría principal
            subcategory: Subcategoría (opcional)
            entities: Entidades detectadas (opcional)
            
        Returns:
            Ruta de categoría sugerida
        """
        path_parts = [primary_category]
        
        if subcategory:
            path_parts.append(subcategory)
        
        # Agregar entidades relevantes a la ruta
        if entities:
            for entity in entities:
                entity_type = entity.get("type", "")
                entity_name = entity.get("name", "")
                
                # Solo agregar personas y proyectos a la ruta
                if entity_type in ["person", "project"] and entity_name:
                    # Limpiar nombre para usar como directorio
                    clean_name = entity_name.replace(" ", "").replace("-", "")
                    path_parts.append(clean_name)
                    break  # Solo agregar la primera entidad relevante
        
        return "/".join(path_parts)
    
    def get_category_hierarchy(self) -> Dict:
        """
        Obtiene la jerarquía completa de categorías
        
        Returns:
            Diccionario con la jerarquía de categorías
        """
        hierarchy = {}
        
        for category, config in self.categories.items():
            hierarchy[category] = {
                "keywords": config["keywords"],
                "weight": config["weight"],
                "subcategories": self.subcategories.get(category, {})
            }
        
        return hierarchy
    
    def update_categories(self, new_categories: Dict):
        """
        Actualiza las categorías con nuevas definiciones
        
        Args:
            new_categories: Nuevas definiciones de categorías
        """
        for category, config in new_categories.items():
            if category in self.categories:
                # Actualizar categoría existente
                self.categories[category].update(config)
            else:
                # Agregar nueva categoría
                self.categories[category] = config

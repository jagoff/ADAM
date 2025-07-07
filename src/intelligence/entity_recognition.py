"""
Sistema de reconocimiento de entidades para ADAM
Detecta personas, fechas, proyectos, etc. en el texto
"""
import re
from typing import List, Dict, Optional
from datetime import datetime

class EntityRecognizer:
    """Reconocedor de entidades para ADAM"""
    
    def __init__(self):
        """Inicializa el reconocedor de entidades"""
        # Patrones para diferentes tipos de entidades
        self.patterns = {
            "person": [
                r"\b[A-Z][a-z]+ [A-Z][a-z]+\b",  # Nombres completos
                r"\b[A-Z][a-z]+\b",  # Nombres simples
            ],
            "date": [
                r"\b\d{1,2}/\d{1,2}/\d{4}\b",  # DD/MM/YYYY
                r"\b\d{4}-\d{2}-\d{2}\b",  # YYYY-MM-DD
                r"\b\d{1,2} de [a-z]+ de \d{4}\b",  # 15 de enero de 2024
                r"\b[a-z]+ \d{1,2},? \d{4}\b",  # January 15, 2024
                r"\bQ[1-4]\b",  # Q1, Q2, Q3, Q4
                r"\b\d{4}\b",  # Años
            ],
            "project": [
                r"\bproyecto [A-Z][a-z]+\b",
                r"\b[A-Z][A-Z]+\b",  # Acrónimos en mayúsculas
                r"\b[A-Z][a-z]+[A-Z][a-z]+\b",  # CamelCase
            ],
            "company": [
                r"\b[A-Z][a-z]+ (Inc|Corp|LLC|Ltd|S\.A\.|S\.A\.S\.)\b",
                r"\b[A-Z][a-z]+ [A-Z][a-z]+ (Company|Corporation|Enterprise)\b",
            ],
            "url": [
                r"https?://[^\s]+",
                r"www\.[^\s]+",
            ],
            "email": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            ],
            "phone": [
                r"\b\+?[\d\s\-\(\)]{10,}\b",
            ],
        }
        
        # Palabras clave para categorización
        self.keywords = {
            "person": ["marco", "maría", "juan", "ana", "pedro", "lisa", "carlos"],
            "project": ["finops", "devops", "frontend", "backend", "api", "database"],
            "company": ["google", "microsoft", "apple", "amazon", "meta"],
            "event": ["reunión", "meeting", "conferencia", "presentación", "demo"],
            "task": ["tarea", "task", "trabajo", "proyecto", "desarrollo"],
        }
    
    async def extract_entities(self, text: str) -> List[Dict]:
        """
        Extrae entidades del texto
        
        Args:
            text: Texto a analizar
            
        Returns:
            Lista de entidades detectadas
        """
        entities = []
        
        # Detectar por patrones regex
        for entity_type, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    entity = {
                        "name": match.group(),
                        "type": entity_type,
                        "start": match.start(),
                        "end": match.end(),
                        "confidence": 0.8,
                        "metadata": {}
                    }
                    entities.append(entity)
        
        # Detectar por palabras clave
        text_lower = text.lower()
        for entity_type, keywords in self.keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Buscar la palabra exacta en el texto original
                    pattern = r"\b" + re.escape(keyword) + r"\b"
                    matches = re.finditer(pattern, text, re.IGNORECASE)
                    for match in matches:
                        entity = {
                            "name": match.group(),
                            "type": entity_type,
                            "start": match.start(),
                            "end": match.end(),
                            "confidence": 0.9,
                            "metadata": {}
                        }
                        entities.append(entity)
        
        # Detectar fechas especiales
        entities.extend(self._extract_special_dates(text))
        
        # Detectar proyectos mencionados
        entities.extend(self._extract_projects(text))
        
        # Remover duplicados y ordenar por posición
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _extract_special_dates(self, text: str) -> List[Dict]:
        """Extrae fechas especiales como cumpleaños, deadlines, etc."""
        entities = []
        
        # Patrones para fechas especiales
        birthday_patterns = [
            r"cumpleaños de ([A-Z][a-z]+)",
            r"birthday of ([A-Z][a-z]+)",
            r"([A-Z][a-z]+) cumple años",
        ]
        
        deadline_patterns = [
            r"deadline ([a-z]+ \d{1,2})",
            r"fecha límite ([a-z]+ \d{1,2})",
            r"entrega ([a-z]+ \d{1,2})",
        ]
        
        for pattern in birthday_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                person_name = match.group(1)
                entities.append({
                    "name": person_name,
                    "type": "person",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.9,
                    "metadata": {"context": "birthday"}
                })
        
        for pattern in deadline_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                date_text = match.group(1)
                entities.append({
                    "name": date_text,
                    "type": "date",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.8,
                    "metadata": {"context": "deadline"}
                })
        
        return entities
    
    def _extract_projects(self, text: str) -> List[Dict]:
        """Extrae proyectos mencionados en el texto"""
        entities = []
        
        # Patrones para proyectos
        project_patterns = [
            r"proyecto ([A-Z][a-z]+)",
            r"project ([A-Z][a-z]+)",
            r"([A-Z][a-z]+) project",
            r"trabajando en ([A-Z][a-z]+)",
            r"desarrollando ([A-Z][a-z]+)",
        ]
        
        for pattern in project_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                project_name = match.group(1)
                entities.append({
                    "name": project_name,
                    "type": "project",
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 0.8,
                    "metadata": {"context": "development"}
                })
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remueve entidades duplicadas y ordena por posición"""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            # Crear clave única basada en nombre, tipo y posición
            key = (entity["name"].lower(), entity["type"], entity["start"])
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        # Ordenar por posición en el texto
        unique_entities.sort(key=lambda x: x["start"])
        
        return unique_entities
    
    def get_entity_statistics(self, entities: List[Dict]) -> Dict:
        """
        Obtiene estadísticas de las entidades detectadas
        
        Args:
            entities: Lista de entidades
            
        Returns:
            Diccionario con estadísticas
        """
        stats = {
            "total": len(entities),
            "by_type": {},
            "confidence_avg": 0.0
        }
        
        if not entities:
            return stats
        
        # Contar por tipo
        for entity in entities:
            entity_type = entity["type"]
            if entity_type not in stats["by_type"]:
                stats["by_type"][entity_type] = 0
            stats["by_type"][entity_type] += 1
        
        # Calcular confianza promedio
        total_confidence = sum(entity["confidence"] for entity in entities)
        stats["confidence_avg"] = total_confidence / len(entities)
        
        return stats

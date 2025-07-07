"""
Sistema de base de datos híbrida para ADAM
SQLite para metadata estructurada y relaciones
"""
import sqlite3
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path

from ..core.config import settings

class DatabaseManager:
    """Gestor de base de datos SQLite para ADAM"""
    
    def __init__(self):
        self.db_path = settings.SQLITE_DB_PATH
        self.ensure_database()
    
    def ensure_database(self):
        """Crea la base de datos y las tablas si no existen"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    timestamp DATETIME,
                    user_message TEXT,
                    adam_response TEXT,
                    entities_json TEXT,
                    chroma_id TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    metadata_json TEXT,
                    first_seen DATETIME,
                    mention_count INTEGER DEFAULT 1
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS files (
                    id TEXT PRIMARY KEY,
                    original_name TEXT,
                    stored_path TEXT,
                    category TEXT,
                    file_hash TEXT,
                    metadata_json TEXT,
                    chroma_id TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS relationships (
                    entity1_id TEXT,
                    entity2_id TEXT,
                    relationship_type TEXT,
                    context TEXT,
                    FOREIGN KEY (entity1_id) REFERENCES entities (id),
                    FOREIGN KEY (entity2_id) REFERENCES entities (id)
                )
            """)
            
            # Índices para mejorar performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_session ON conversations(session_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_entities_type ON entities(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_files_category ON files(category)")
            
            conn.commit()
    
    def save_conversation(
        self,
        session_id: str,
        user_message: str,
        adam_response: str,
        entities: Optional[List[Dict]] = None,
        chroma_id: Optional[str] = None
    ) -> str:
        """Guarda una conversación en la base de datos"""
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        entities_json = json.dumps(entities) if entities else None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO conversations 
                (id, session_id, timestamp, user_message, adam_response, entities_json, chroma_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (conversation_id, session_id, timestamp, user_message, adam_response, entities_json, chroma_id))
            conn.commit()
        
        return conversation_id
    
    def get_conversation_history(
        self,
        session_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Obtiene el historial de conversaciones"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if session_id:
                cursor = conn.execute("""
                    SELECT * FROM conversations 
                    WHERE session_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (session_id, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM conversations 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """, (limit,))
            
            conversations = []
            for row in cursor.fetchall():
                conv = dict(row)
                if conv['entities_json']:
                    conv['entities'] = json.loads(conv['entities_json'])
                else:
                    conv['entities'] = []
                conversations.append(conv)
            
            return conversations
    
    def save_entity(
        self,
        name: str,
        entity_type: str,
        metadata: Optional[Dict] = None
    ) -> str:
        """Guarda o actualiza una entidad"""
        entity_id = str(uuid.uuid4())
        metadata_json = json.dumps(metadata) if metadata else None
        first_seen = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Verificar si la entidad ya existe
            cursor = conn.execute(
                "SELECT id, mention_count FROM entities WHERE name = ? AND type = ?",
                (name, entity_type)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Actualizar contador de menciones
                conn.execute(
                    "UPDATE entities SET mention_count = mention_count + 1 WHERE id = ?",
                    (existing[0],)
                )
                entity_id = existing[0]
            else:
                # Crear nueva entidad
                conn.execute("""
                    INSERT INTO entities 
                    (id, name, type, metadata_json, first_seen, mention_count)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (entity_id, name, entity_type, metadata_json, first_seen, 1))
            
            conn.commit()
        
        return entity_id
    
    def get_entities(
        self,
        entity_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """Obtiene entidades de la base de datos"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if entity_type:
                cursor = conn.execute("""
                    SELECT * FROM entities 
                    WHERE type = ? 
                    ORDER BY mention_count DESC, first_seen DESC 
                    LIMIT ?
                """, (entity_type, limit))
            else:
                cursor = conn.execute("""
                    SELECT * FROM entities 
                    ORDER BY mention_count DESC, first_seen DESC 
                    LIMIT ?
                """, (limit,))
            
            entities = []
            for row in cursor.fetchall():
                entity = dict(row)
                if entity['metadata_json']:
                    entity['metadata'] = json.loads(entity['metadata_json'])
                else:
                    entity['metadata'] = {}
                entities.append(entity)
            
            return entities
    
    def save_file(
        self,
        original_name: str,
        stored_path: str,
        category: str,
        file_hash: str,
        metadata: Optional[Dict] = None,
        chroma_id: Optional[str] = None
    ) -> str:
        """Guarda información de un archivo"""
        file_id = str(uuid.uuid4())
        metadata_json = json.dumps(metadata) if metadata else None
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO files 
                (id, original_name, stored_path, category, file_hash, metadata_json, chroma_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (file_id, original_name, stored_path, category, file_hash, metadata_json, chroma_id))
            conn.commit()
        
        return file_id
    
    def save_relationship(
        self,
        entity1_id: str,
        entity2_id: str,
        relationship_type: str,
        context: Optional[str] = None
    ):
        """Guarda una relación entre entidades"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO relationships 
                (entity1_id, entity2_id, relationship_type, context)
                VALUES (?, ?, ?, ?)
            """, (entity1_id, entity2_id, relationship_type, context))
            conn.commit()
    
    def get_relationships(
        self,
        entity_id: str
    ) -> List[Dict]:
        """Obtiene las relaciones de una entidad"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT r.*, e1.name as entity1_name, e2.name as entity2_name
                FROM relationships r
                JOIN entities e1 ON r.entity1_id = e1.id
                JOIN entities e2 ON r.entity2_id = e2.id
                WHERE r.entity1_id = ? OR r.entity2_id = ?
            """, (entity_id, entity_id))
            
            relationships = []
            for row in cursor.fetchall():
                relationships.append(dict(row))
            
            return relationships

# Instancia global del gestor de base de datos
db_manager = DatabaseManager()

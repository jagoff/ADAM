# ADAM - Artificial Digital Assistant for Memory

## Visión General
ADAM es un asistente de IA personal que funciona como un "segundo cerebro digital". A diferencia de otros asistentes, ADAM está diseñado para recordar TODO lo que el usuario le comparte, organizarlo inteligentemente y proporcionar coaching proactivo basado en el conocimiento acumulado.

## Concepto Core
- **Memoria Perfecta**: ADAM nunca olvida nada
- **Organización Orgánica**: Las categorías emergen naturalmente basadas en el uso
- **Coaching Proactivo**: No espera comandos, anticipa necesidades
- **100% Local**: Privacidad total, todos los datos en la máquina del usuario

## Características Principales

### 1. Ingestión Universal
- Acepta CUALQUIER tipo de input: texto, imágenes, PDFs, links, notas de voz
- Sin fricción: el usuario puede "tirar" cualquier cosa a ADAM
- Detección automática de tipo de contenido
- Extracción inteligente de información

### 2. Memoria Contextual
- Recuerda no solo QUÉ sino CUÁNDO, CÓMO y POR QUÉ
- Tracking de personas, proyectos, fechas importantes
- Construcción de grafos de relaciones
- Análisis de patrones de comportamiento

### 3. Biblioteca Auto-Organizada
- Estructura de carpetas que emerge del uso
- Categorización multi-dimensional (un item puede estar en varios lugares)
- Ejemplos de categorías emergentes:
  - `/Family/Maria/` (cumpleaños, conversaciones, fotos)
  - `/Work/Projects/FinOps/` (meetings, decisiones, documentos)
  - `/Links/Development/` (recursos guardados)

### 4. Coaching Inteligente (Sparring Partner)
- Personalidad propia: directa pero empática
- Ejemplos de proactividad:
  - "¿Cómo estuvo tu reunión con Marco sobre FinOps?"
  - "Recuerda que el 15 María cumple años"
  - "Basándome en patrones, tu productividad es mejor entre 10-12am"
- Detecta patrones y sugiere mejoras

## Stack Técnico

### Backend
```python
# Core
- Python 3.11+
- FastAPI (API REST)
- Anthropic API (Claude Opus 4)

# Bases de Datos (100% local)
- ChromaDB (búsqueda semántica y vectores)
- SQLite (metadata estructurada, relaciones)

# Procesamiento
- PyPDF (extracción de PDFs)
- Pillow (procesamiento de imágenes)
- Whisper (futuro: transcripción de audio)

# Utilidades
- aiofiles (manejo async de archivos)
- pydantic (validación de datos)
- watchdog (monitor de cambios)
```

## Arquitectura

```
adam/
├── adam_data/                    # Datos del usuario
│   ├── adam.db                   # SQLite principal
│   ├── chroma/                   # Vectores ChromaDB
│   └── library/                  # Archivos organizados
│       ├── documents/
│       ├── images/
│       └── [categorías emergentes]/
├── src/
│   ├── core/                     # Núcleo de ADAM
│   │   ├── adam.py              # Clase principal
│   │   └── config.py            # Configuración
│   ├── memory/                   # Sistema de memoria
│   │   ├── memory_system.py     # Gestión de memoria
│   │   ├── contextual.py        # Memoria contextual
│   │   └── embeddings.py        # Vectorización
│   ├── intelligence/             # IA y procesamiento
│   │   ├── entity_recognition.py # Detección de entidades
│   │   ├── categorizer.py       # Categorización automática
│   │   └── coach.py             # Sistema de coaching
│   ├── storage/                  # Almacenamiento
│   │   ├── local_storage.py     # Sistema de archivos
│   │   └── database.py          # Gestión BD híbrida
│   └── api/                      # Endpoints
│       ├── chat.py              # Chat principal
│       └── library.py           # Gestión de biblioteca
├── main.py                       # Entrada principal
└── requirements.txt
```

## Modelos de Datos

### SQLite Schema
```sql
-- Conversaciones
CREATE TABLE conversations (
    id TEXT PRIMARY KEY,
    session_id TEXT,
    timestamp DATETIME,
    user_message TEXT,
    adam_response TEXT,
    entities_json TEXT,  -- Personas, fechas, proyectos detectados
    chroma_id TEXT       -- Link al vector en ChromaDB
);

-- Entidades (personas, proyectos, etc)
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    name TEXT,
    type TEXT,           -- person, project, company, event
    metadata_json TEXT,  -- Info adicional flexible
    first_seen DATETIME,
    mention_count INTEGER
);

-- Archivos
CREATE TABLE files (
    id TEXT PRIMARY KEY,
    original_name TEXT,
    stored_path TEXT,
    category TEXT,
    file_hash TEXT,
    metadata_json TEXT,
    chroma_id TEXT
);

-- Relaciones
CREATE TABLE relationships (
    entity1_id TEXT,
    entity2_id TEXT,
    relationship_type TEXT,
    context TEXT
);
```

### ChromaDB Collections
```python
collections = {
    "conversations": {
        "metadata": ["session_id", "timestamp", "entities"],
        "embeddings": "all-MiniLM-L6-v2"
    },
    "documents": {
        "metadata": ["file_type", "category", "date"],
        "embeddings": "all-mpnet-base-v2"
    },
    "knowledge": {
        "metadata": ["topic", "source", "confidence"],
        "embeddings": "all-mpnet-base-v2"
    }
}
```

## Flujos Principales

### 1. Chat con Memoria
```python
User: "Reunión con Marco sobre presupuestos del Q2"

ADAM: 
1. Extrae entidades: Marco (persona), Q2 (tiempo), presupuestos (tema)
2. Busca contexto previo sobre Marco y presupuestos
3. Genera respuesta contextual
4. Almacena en memoria con todos los metadatos
5. Programa recordatorios si detecta compromisos
```

### 2. Ingestión de Archivo
```python
User: [Sube PDF de propuesta]

ADAM:
1. Extrae texto del PDF
2. Identifica: tipo de documento, personas mencionadas, fechas
3. Lo categoriza automáticamente
4. Crea embeddings para búsqueda
5. Conecta con conocimiento existente
6. Responde: "Guardé la propuesta. Veo que menciona el proyecto 
   FinOps que discutiste con Marco la semana pasada."
```

### 3. Coaching Proactivo
```python
ADAM (8:30 AM): "Buenos días! Basándome en tu calendario:
- Reunión con Marco a las 3pm (preparé un resumen)
- María cumple años en 3 días
- Llevas 3 días sin respuesta de Juan sobre los mockups
¿Algo más que deba tener en cuenta para hoy?"
```

## Roadmap de Desarrollo

### Fase 1: Foundation (Actual)
- [x] Estructura del proyecto
- [x] Configuración base
- [ ] Chat básico funcional
- [ ] Almacenamiento de conversaciones
- [ ] API REST simple

### Fase 2: Memory System
- [ ] ChromaDB integrado
- [ ] Búsqueda semántica
- [ ] Extracción de entidades
- [ ] Memoria persistente entre sesiones

### Fase 3: Intelligence
- [ ] Categorización automática
- [ ] Detección de patrones
- [ ] Sistema de relaciones
- [ ] Insights básicos

### Fase 4: Coaching
- [ ] Recordatorios inteligentes
- [ ] Daily brief automático
- [ ] Sugerencias proactivas
- [ ] Análisis de productividad

### Fase 5: Advanced
- [ ] Procesamiento de imágenes
- [ ] Transcripción de audio
- [ ] UI web básica
- [ ] Exportación de conocimiento

## Principios de Diseño

1. **"Todo es valioso"**: ADAM nunca rechaza información
2. **"Sin fricción"**: Agregar info debe ser instantáneo
3. **"Privacidad primero"**: 100% local, sin cloud
4. **"Contexto es rey"**: No solo qué, sino cuándo, dónde, por qué
5. **"Evolución orgánica"**: La estructura emerge del uso

## Estado Actual

- **Completado**: Arquitectura, estructura, configuración base
- **En progreso**: Sistema de chat básico, almacenamiento local
- **Siguiente**: Integración ChromaDB, extracción de entidades

## Instrucciones para Continuar

1. El proyecto se llama **ADAM** (no adam-mvp)
2. Mantener enfoque 100% local
3. Priorizar funcionalidad sobre UI
4. Cada componente debe ser testeable
5. Documentar decisiones importantes

## Ejemplo de Uso Objetivo

```python
# El usuario puede interactuar así:
"Guardar este link sobre Python async"
"Foto de Astor en el parque" + [imagen]
"Reunión con María sobre el proyecto X, decidimos postponer 2 semanas"
"¿Qué hablé con Marco sobre presupuestos?"
"¿Cuándo es el cumpleaños de María?"
"Dame un resumen de lo que pasó esta semana"
```

ADAM responde con contexto completo, hace conexiones inteligentes y sugiere acciones proactivamente. 
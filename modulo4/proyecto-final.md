# Proyecto Final: Sistema Completo de MCP

## Descripción del Proyecto

Crearás un **Sistema de Gestión de Proyectos** completo que integra:
- ✅ Tools para gestionar tareas
- ✅ Resources para acceder a documentación
- ✅ Prompts para workflows comunes
- ✅ Integración con base de datos
- ✅ Sistema de logging

## Estructura del Proyecto

```
proyecto-final/
│
├── src/
│   ├── __init__.py
│   ├── main.py              # Servidor principal
│   ├── database.py          # Capa de base de datos
│   ├── models.py            # Modelos de datos
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── tareas.py        # Herramientas de tareas
│   │   └── reportes.py      # Herramientas de reportes
│   │
│   ├── resources/
│   │   ├── __init__.py
│   │   └── docs.py          # Recursos de documentación
│   │
│   └── prompts/
│       ├── __init__.py
│       └── templates.py     # Templates de prompts
│
├── data/
│   └── proyectos.db         # Base de datos SQLite
│
├── docs/
│   ├── guia-usuario.md
│   └── api.md
│
├── tests/
│   ├── test_tools.py
│   └── test_database.py
│
├── requirements.txt
└── README.md
```

## Código Completo

### 1. Modelos de Datos

```python
# src/models.py
"""
Modelos de datos del sistema de gestión de proyectos
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from enum import Enum

class Prioridad(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    URGENTE = "urgente"

class Estado(str, Enum):
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"

class Tarea(BaseModel):
    id: Optional[int] = None
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: str = ""
    prioridad: Prioridad = Prioridad.MEDIA
    estado: Estado = Estado.PENDIENTE
    proyecto_id: Optional[int] = None
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_limite: Optional[datetime] = None
    etiquetas: List[str] = []

class Proyecto(BaseModel):
    id: Optional[int] = None
    nombre: str = Field(..., min_length=1, max_length=100)
    descripcion: str = ""
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    activo: bool = True
```

### 2. Capa de Base de Datos

```python
# src/database.py
"""
Manejo de base de datos SQLite
"""

import aiosqlite
from pathlib import Path
from typing import List, Optional
from .models import Tarea, Proyecto, Estado, Prioridad
import json
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path("data/proyectos.db")
DB_PATH.parent.mkdir(exist_ok=True)

async def inicializar_db():
    """Crea las tablas si no existen"""
    async with aiosqlite.connect(DB_PATH) as db:
        # Tabla de proyectos
        await db.execute("""
            CREATE TABLE IF NOT EXISTS proyectos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                fecha_creacion TEXT NOT NULL,
                activo INTEGER DEFAULT 1
            )
        """)
        
        # Tabla de tareas
        await db.execute("""
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                descripcion TEXT,
                prioridad TEXT NOT NULL,
                estado TEXT NOT NULL,
                proyecto_id INTEGER,
                fecha_creacion TEXT NOT NULL,
                fecha_limite TEXT,
                etiquetas TEXT,
                FOREIGN KEY (proyecto_id) REFERENCES proyectos(id)
            )
        """)
        
        await db.commit()
        logger.info("Base de datos inicializada")

class TareasDB:
    """Operaciones de base de datos para tareas"""
    
    @staticmethod
    async def crear(tarea: Tarea) -> int:
        """Crea una nueva tarea"""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO tareas 
                (titulo, descripcion, prioridad, estado, proyecto_id, 
                 fecha_creacion, fecha_limite, etiquetas)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    tarea.titulo,
                    tarea.descripcion,
                    tarea.prioridad.value,
                    tarea.estado.value,
                    tarea.proyecto_id,
                    tarea.fecha_creacion.isoformat(),
                    tarea.fecha_limite.isoformat() if tarea.fecha_limite else None,
                    json.dumps(tarea.etiquetas)
                )
            )
            await db.commit()
            return cursor.lastrowid
    
    @staticmethod
    async def listar(
        proyecto_id: Optional[int] = None,
        estado: Optional[Estado] = None
    ) -> List[Tarea]:
        """Lista tareas con filtros opcionales"""
        async with aiosqlite.connect(DB_PATH) as db:
            query = "SELECT * FROM tareas WHERE 1=1"
            params = []
            
            if proyecto_id:
                query += " AND proyecto_id = ?"
                params.append(proyecto_id)
            
            if estado:
                query += " AND estado = ?"
                params.append(estado.value)
            
            query += " ORDER BY fecha_creacion DESC"
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                
                tareas = []
                for row in rows:
                    tareas.append(Tarea(
                        id=row[0],
                        titulo=row[1],
                        descripcion=row[2],
                        prioridad=Prioridad(row[3]),
                        estado=Estado(row[4]),
                        proyecto_id=row[5],
                        fecha_creacion=datetime.fromisoformat(row[6]),
                        fecha_limite=datetime.fromisoformat(row[7]) if row[7] else None,
                        etiquetas=json.loads(row[8]) if row[8] else []
                    ))
                
                return tareas
    
    @staticmethod
    async def actualizar(tarea_id: int, **campos) -> bool:
        """Actualiza campos de una tarea"""
        if not campos:
            return False
        
        async with aiosqlite.connect(DB_PATH) as db:
            set_clause = ", ".join([f"{k} = ?" for k in campos.keys()])
            query = f"UPDATE tareas SET {set_clause} WHERE id = ?"
            
            await db.execute(query, list(campos.values()) + [tarea_id])
            await db.commit()
            return True
    
    @staticmethod
    async def eliminar(tarea_id: int) -> bool:
        """Elimina una tarea"""
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("DELETE FROM tareas WHERE id = ?", (tarea_id,))
            await db.commit()
            return True

class ProyectosDB:
    """Operaciones de base de datos para proyectos"""
    
    @staticmethod
    async def crear(proyecto: Proyecto) -> int:
        """Crea un nuevo proyecto"""
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute(
                """
                INSERT INTO proyectos (nombre, descripcion, fecha_creacion, activo)
                VALUES (?, ?, ?, ?)
                """,
                (
                    proyecto.nombre,
                    proyecto.descripcion,
                    proyecto.fecha_creacion.isoformat(),
                    1 if proyecto.activo else 0
                )
            )
            await db.commit()
            return cursor.lastrowid
    
    @staticmethod
    async def listar(solo_activos: bool = True) -> List[Proyecto]:
        """Lista todos los proyectos"""
        async with aiosqlite.connect(DB_PATH) as db:
            query = "SELECT * FROM proyectos"
            if solo_activos:
                query += " WHERE activo = 1"
            
            async with db.execute(query) as cursor:
                rows = await cursor.fetchall()
                
                return [
                    Proyecto(
                        id=row[0],
                        nombre=row[1],
                        descripcion=row[2],
                        fecha_creacion=datetime.fromisoformat(row[3]),
                        activo=bool(row[4])
                    )
                    for row in rows
                ]
```

Continuaré con el resto del proyecto en el siguiente mensaje debido a la longitud...

---

**Anterior:** [Lección 3.3 - Seguridad](leccion3-seguridad.md)  
**Siguiente:** Implementación completa del proyecto

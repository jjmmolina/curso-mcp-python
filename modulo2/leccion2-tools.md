# Lección 2.2: Implementando Tools (Herramientas)

## Introducción

Las **herramientas (tools)** son el corazón de un servidor MCP. Permiten que los modelos de IA ejecuten acciones específicas. En esta lección aprenderemos a crear herramientas robustas y útiles.

## Tipos de Herramientas

### 1. Herramientas de Lectura
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "obtener_clima":
        # Solo lectura, sin efectos secundarios
        return datos_clima
```

### 2. Herramientas de Escritura
```python
if name == "guardar_nota":
    # Modifica datos
    await guardar_en_bd(nota)
```

### 3. Herramientas de Acción
```python
if name == "enviar_email":
    # Ejecuta una acción
    await enviar_correo(destinatario, mensaje)
```

## Ejemplo Completo: Sistema de Notas

```python
# src/tools/notas_server.py
"""
Servidor MCP para gestión de notas
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, McpError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Modelos de datos
class Nota(BaseModel):
    id: str
    titulo: str
    contenido: str
    fecha_creacion: str
    etiquetas: List[str] = []

class CrearNotaArgs(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=100)
    contenido: str = Field(..., min_length=1)
    etiquetas: Optional[List[str]] = []

class BuscarNotasArgs(BaseModel):
    termino: str = Field(..., min_length=1)

class EliminarNotaArgs(BaseModel):
    id: str

# Almacenamiento (en un proyecto real, usar base de datos)
NOTAS_FILE = Path("data/notas.json")
NOTAS_FILE.parent.mkdir(exist_ok=True)

def cargar_notas() -> List[Nota]:
    """Carga las notas desde el archivo"""
    if not NOTAS_FILE.exists():
        return []
    
    try:
        with open(NOTAS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return [Nota(**nota) for nota in data]
    except Exception as e:
        logger.error(f"Error cargando notas: {e}")
        return []

def guardar_notas(notas: List[Nota]):
    """Guarda las notas en el archivo"""
    try:
        with open(NOTAS_FILE, 'w', encoding='utf-8') as f:
            data = [nota.dict() for nota in notas]
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando notas: {e}")
        raise

# Crear servidor
server = Server("notas-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Lista todas las herramientas disponibles"""
    return [
        Tool(
            name="crear_nota",
            description="Crea una nueva nota con título, contenido y etiquetas opcionales",
            inputSchema={
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "Título de la nota (máx. 100 caracteres)",
                        "minLength": 1,
                        "maxLength": 100
                    },
                    "contenido": {
                        "type": "string",
                        "description": "Contenido de la nota",
                        "minLength": 1
                    },
                    "etiquetas": {
                        "type": "array",
                        "description": "Lista de etiquetas para organizar la nota",
                        "items": {"type": "string"},
                        "default": []
                    }
                },
                "required": ["titulo", "contenido"]
            }
        ),
        Tool(
            name="listar_notas",
            description="Lista todas las notas guardadas",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="buscar_notas",
            description="Busca notas por término en título o contenido",
            inputSchema={
                "type": "object",
                "properties": {
                    "termino": {
                        "type": "string",
                        "description": "Término a buscar",
                        "minLength": 1
                    }
                },
                "required": ["termino"]
            }
        ),
        Tool(
            name="eliminar_nota",
            description="Elimina una nota por su ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID de la nota a eliminar"
                    }
                },
                "required": ["id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Ejecuta la herramienta solicitada"""
    
    try:
        if name == "crear_nota":
            return await crear_nota(arguments)
        elif name == "listar_notas":
            return await listar_notas()
        elif name == "buscar_notas":
            return await buscar_notas(arguments)
        elif name == "eliminar_nota":
            return await eliminar_nota(arguments)
        else:
            raise McpError(
                code=-32601,
                message=f"Herramienta no encontrada: {name}"
            )
    
    except McpError:
        raise
    except ValueError as e:
        raise McpError(code=-32602, message=str(e))
    except Exception as e:
        logger.error(f"Error en {name}: {e}", exc_info=True)
        raise McpError(code=-32603, message="Error interno del servidor")

async def crear_nota(arguments: dict) -> List[TextContent]:
    """Crea una nueva nota"""
    args = CrearNotaArgs(**arguments)
    
    # Cargar notas existentes
    notas = cargar_notas()
    
    # Crear nueva nota
    nueva_nota = Nota(
        id=f"nota_{datetime.now().timestamp()}",
        titulo=args.titulo,
        contenido=args.contenido,
        fecha_creacion=datetime.now().isoformat(),
        etiquetas=args.etiquetas or []
    )
    
    # Agregar y guardar
    notas.append(nueva_nota)
    guardar_notas(notas)
    
    logger.info(f"Nota creada: {nueva_nota.id}")
    
    return [TextContent(
        type="text",
        text=f"✅ Nota creada exitosamente!\n\n"
             f"ID: {nueva_nota.id}\n"
             f"Título: {nueva_nota.titulo}\n"
             f"Etiquetas: {', '.join(nueva_nota.etiquetas) if nueva_nota.etiquetas else 'Ninguna'}"
    )]

async def listar_notas() -> List[TextContent]:
    """Lista todas las notas"""
    notas = cargar_notas()
    
    if not notas:
        return [TextContent(
            type="text",
            text="📝 No hay notas guardadas."
        )]
    
    # Formatear lista de notas
    resultado = f"📝 Tienes {len(notas)} nota(s):\n\n"
    
    for nota in notas:
        etiquetas = f"[{', '.join(nota.etiquetas)}]" if nota.etiquetas else ""
        resultado += f"• {nota.titulo} {etiquetas}\n"
        resultado += f"  ID: {nota.id}\n"
        resultado += f"  Creada: {nota.fecha_creacion}\n"
        resultado += f"  {nota.contenido[:100]}{'...' if len(nota.contenido) > 100 else ''}\n\n"
    
    return [TextContent(type="text", text=resultado)]

async def buscar_notas(arguments: dict) -> List[TextContent]:
    """Busca notas por término"""
    args = BuscarNotasArgs(**arguments)
    notas = cargar_notas()
    
    termino_lower = args.termino.lower()
    
    # Buscar en título y contenido
    encontradas = [
        nota for nota in notas
        if termino_lower in nota.titulo.lower() or 
           termino_lower in nota.contenido.lower()
    ]
    
    if not encontradas:
        return [TextContent(
            type="text",
            text=f"🔍 No se encontraron notas con el término '{args.termino}'."
        )]
    
    resultado = f"🔍 Se encontraron {len(encontradas)} nota(s) con '{args.termino}':\n\n"
    
    for nota in encontradas:
        resultado += f"• {nota.titulo}\n"
        resultado += f"  ID: {nota.id}\n"
        resultado += f"  {nota.contenido[:150]}{'...' if len(nota.contenido) > 150 else ''}\n\n"
    
    return [TextContent(type="text", text=resultado)]

async def eliminar_nota(arguments: dict) -> List[TextContent]:
    """Elimina una nota por ID"""
    args = EliminarNotaArgs(**arguments)
    notas = cargar_notas()
    
    # Buscar y eliminar
    notas_filtradas = [nota for nota in notas if nota.id != args.id]
    
    if len(notas_filtradas) == len(notas):
        return [TextContent(
            type="text",
            text=f"❌ No se encontró una nota con ID: {args.id}"
        )]
    
    guardar_notas(notas_filtradas)
    logger.info(f"Nota eliminada: {args.id}")
    
    return [TextContent(
        type="text",
        text=f"🗑️ Nota eliminada exitosamente (ID: {args.id})"
    )]

async def main():
    """Punto de entrada del servidor"""
    logger.info("Iniciando servidor de notas MCP...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Mejores Prácticas para Tools

### 1. Nombres Descriptivos

```python
# ❌ Malo
Tool(name="fn1", description="hace algo")

# ✅ Bueno
Tool(
    name="calcular_impuesto",
    description="Calcula el impuesto sobre ventas para un monto dado"
)
```

### 2. Descripciones Claras

```python
Tool(
    name="convertir_moneda",
    description="Convierte una cantidad de una moneda a otra usando tasas de cambio actuales. "
                "Soporta USD, EUR, GBP, JPY. Requiere conexión a internet."
)
```

### 3. Schemas Bien Definidos

```python
inputSchema={
    "type": "object",
    "properties": {
        "cantidad": {
            "type": "number",
            "description": "Cantidad a convertir (debe ser positiva)",
            "minimum": 0
        },
        "de": {
            "type": "string",
            "description": "Moneda origen",
            "enum": ["USD", "EUR", "GBP", "JPY"]
        },
        "a": {
            "type": "string",
            "description": "Moneda destino",
            "enum": ["USD", "EUR", "GBP", "JPY"]
        }
    },
    "required": ["cantidad", "de", "a"]
}
```

### 4. Validación con Pydantic

```python
from pydantic import BaseModel, Field, validator

class ConvertirMonedaArgs(BaseModel):
    cantidad: float = Field(gt=0, description="Cantidad positiva")
    de: str = Field(..., regex="^(USD|EUR|GBP|JPY)$")
    a: str = Field(..., regex="^(USD|EUR|GBP|JPY)$")
    
    @validator('a')
    def monedas_diferentes(cls, v, values):
        if 'de' in values and v == values['de']:
            raise ValueError('Las monedas deben ser diferentes')
        return v
```

### 5. Manejo de Errores Específico

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        if name == "dividir":
            a = arguments["a"]
            b = arguments["b"]
            
            if b == 0:
                return [TextContent(
                    type="text",
                    text="❌ Error: No se puede dividir por cero"
                )]
            
            resultado = a / b
            return [TextContent(
                type="text",
                text=f"{a} ÷ {b} = {resultado}"
            )]
    
    except KeyError as e:
        raise McpError(
            code=-32602,
            message=f"Parámetro faltante: {e}"
        )
```

### 6. Respuestas Formateadas

```python
# ✅ Usa emojis y formato claro
return [TextContent(
    type="text",
    text="✅ Operación exitosa!\n\n"
         "📊 Resultados:\n"
         f"   • Total: ${total:,.2f}\n"
         f"   • Impuesto: ${impuesto:,.2f}\n"
         f"   • Subtotal: ${subtotal:,.2f}"
)]
```

## Herramientas Asíncronas

### Operaciones I/O

```python
import aiofiles
import httpx

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "leer_archivo":
        async with aiofiles.open(arguments["ruta"], 'r') as f:
            contenido = await f.read()
        return [TextContent(type="text", text=contenido)]
    
    elif name == "consultar_api":
        async with httpx.AsyncClient() as client:
            response = await client.get(arguments["url"])
            return [TextContent(
                type="text",
                text=response.text
            )]
```

## 📝 Ejercicios

### Ejercicio 1: Lista de Tareas
Crea un servidor MCP con herramientas para:
- Crear tarea (con prioridad: baja, media, alta)
- Listar tareas
- Marcar tarea como completada
- Eliminar tarea
- Filtrar por prioridad

### Ejercicio 2: Conversor Avanzado
Crea herramientas para:
- Convertir temperatura (C, F, K)
- Convertir distancia (m, km, mi, ft)
- Convertir peso (kg, lb, oz)
- Convertir volumen (L, gal, ml)

### Ejercicio 3: Generador de Reportes
Crea una herramienta que:
- Genere reportes en diferentes formatos (texto, markdown, JSON)
- Incluya estadísticas básicas
- Guarde reportes en archivos

---

**Anterior:** [Lección 2.1 - Primer Servidor](leccion1-primer-servidor.md)  
**Siguiente:** [Lección 2.3 - Trabajando con Resources](leccion3-resources.md)

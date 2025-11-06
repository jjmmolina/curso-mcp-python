"""
Servidor MCP para gestión de notas (ejemplo Módulo 2)
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
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

# Almacenamiento
NOTAS_FILE = Path("data/notas.json")
NOTAS_FILE.parent.mkdir(exist_ok=True)

def cargar_notas() -> List[Nota]:
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
    try:
        with open(NOTAS_FILE, 'w', encoding='utf-8') as f:
            data = [nota.model_dump() for nota in notas]
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando notas: {e}")
        raise

# Servidor
server = Server("notas-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    return [
        Tool(
            name="crear_nota",
            description="Crea una nueva nota con título, contenido y etiquetas opcionales",
            inputSchema={
                "type": "object",
                "properties": {
                    "titulo": {"type": "string", "minLength": 1, "maxLength": 100},
                    "contenido": {"type": "string", "minLength": 1},
                    "etiquetas": {"type": "array", "items": {"type": "string"}, "default": []}
                },
                "required": ["titulo", "contenido"]
            }
        ),
        Tool(
            name="listar_notas",
            description="Lista todas las notas guardadas",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="buscar_notas",
            description="Busca notas por término en título o contenido",
            inputSchema={
                "type": "object",
                "properties": {"termino": {"type": "string", "minLength": 1}},
                "required": ["termino"]
            }
        ),
        Tool(
            name="eliminar_nota",
            description="Elimina una nota por su ID",
            inputSchema={
                "type": "object",
                "properties": {"id": {"type": "string"}},
                "required": ["id"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Ejecuta la herramienta solicitada"""
    try:
        if name == "crear_nota":
            return await crear_nota(arguments)
        if name == "listar_notas":
            return await listar_notas()
        if name == "buscar_notas":
            return await buscar_notas(arguments)
        if name == "eliminar_nota":
            return await eliminar_nota(arguments)
        # Herramienta no encontrada
        logger.error(f"Herramienta no encontrada: {name}")
        return [TextContent(type="text", text=f"❌ Error: Herramienta no encontrada: {name}")]
    except ValueError as e:
        logger.error(f"Error de validación en {name}: {e}")
        return [TextContent(type="text", text=f"❌ Error de validación: {str(e)}")]
    except Exception as e:
        logger.error(f"Error en {name}: {e}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error interno del servidor: {str(e)}")]

async def crear_nota(arguments: dict) -> List[TextContent]:
    args = CrearNotaArgs(**arguments)
    notas = cargar_notas()
    nueva_nota = Nota(
        id=f"nota_{datetime.now().timestamp()}",
        titulo=args.titulo,
        contenido=args.contenido,
        fecha_creacion=datetime.now().isoformat(),
        etiquetas=args.etiquetas or []
    )
    notas.append(nueva_nota)
    guardar_notas(notas)
    return [TextContent(type="text", text=f"✅ Nota creada\nID: {nueva_nota.id}\nTítulo: {nueva_nota.titulo}")]

async def listar_notas() -> List[TextContent]:
    notas = cargar_notas()
    if not notas:
        return [TextContent(type="text", text="📝 No hay notas guardadas.")]
    resultado = [
        "📝 Lista de notas:",
        "",
    ]
    for n in notas:
        etiquetas = f"[{', '.join(n.etiquetas)}]" if n.etiquetas else ""
        resultado.append(f"• {n.titulo} {etiquetas}\n  ID: {n.id}\n  Creada: {n.fecha_creacion}")
    return [TextContent(type="text", text="\n".join(resultado))]

async def buscar_notas(arguments: dict) -> List[TextContent]:
    args = BuscarNotasArgs(**arguments)
    notas = cargar_notas()
    t = args.termino.lower()
    encontradas = [n for n in notas if t in n.titulo.lower() or t in n.contenido.lower()]
    if not encontradas:
        return [TextContent(type="text", text=f"🔍 Sin resultados para '{args.termino}'.")]
    texto = "\n\n".join([f"• {n.titulo}\n  ID: {n.id}" for n in encontradas])
    return [TextContent(type="text", text=f"🔍 Resultados para '{args.termino}':\n\n{texto}")]

async def eliminar_nota(arguments: dict) -> List[TextContent]:
    args = EliminarNotaArgs(**arguments)
    notas = cargar_notas()
    nuevas = [n for n in notas if n.id != args.id]
    if len(nuevas) == len(notas):
        return [TextContent(type="text", text=f"❌ No se encontró nota con ID: {args.id}")]
    guardar_notas(nuevas)
    return [TextContent(type="text", text=f"🗑️ Nota eliminada (ID: {args.id})")]

async def main():
    logger.info("Iniciando servidor de notas MCP...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())

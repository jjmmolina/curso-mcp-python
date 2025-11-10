"""
Servidor MCP para gestión de notas (ejemplo Módulo 2)
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from mcp.fastmcp import FastMCP
from mcp.types import TextContent
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

# Servidor con FastMCP
server = FastMCP(
    "notas-mcp",
    "Un servidor para gestionar una lista de notas.",
)

@server.tool()
async def crear_nota(
    titulo: str = Field(..., description="Título de la nota", min_length=1, max_length=100),
    contenido: str = Field(..., description="Contenido de la nota", min_length=1),
    etiquetas: Optional[List[str]] = Field(None, description="Etiquetas opcionales para la nota")
) -> List[TextContent]:
    """Crea una nueva nota con título, contenido y etiquetas opcionales."""
    try:
        notas = cargar_notas()
        nueva_nota = Nota(
            id=f"nota_{datetime.now().timestamp()}",
            titulo=titulo,
            contenido=contenido,
            fecha_creacion=datetime.now().isoformat(),
            etiquetas=etiquetas or []
        )
        notas.append(nueva_nota)
        guardar_notas(notas)
        return [TextContent(type="text", text=f"✅ Nota creada\nID: {nueva_nota.id}\nTítulo: {nueva_nota.titulo}")]
    except Exception as e:
        logger.error(f"Error en crear_nota: {e}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error interno al crear la nota: {str(e)}")]

@server.tool()
async def listar_notas() -> List[TextContent]:
    """Lista todas las notas guardadas."""
    try:
        notas = cargar_notas()
        if not notas:
            return [TextContent(type="text", text="📝 No hay notas guardadas.")]
        
        resultado = ["📝 Lista de notas:", ""]
        for n in notas:
            etiquetas_str = f"[{', '.join(n.etiquetas)}]" if n.etiquetas else ""
            resultado.append(f"• {n.titulo} {etiquetas_str}\n  ID: {n.id}\n  Creada: {n.fecha_creacion}")
        
        return [TextContent(type="text", text="\n".join(resultado))]
    except Exception as e:
        logger.error(f"Error en listar_notas: {e}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error interno al listar las notas: {str(e)}")]

@server.tool()
async def buscar_notas(termino: str = Field(..., description="Término a buscar en títulos o contenidos", min_length=1)) -> List[TextContent]:
    """Busca notas por término en título o contenido."""
    try:
        notas = cargar_notas()
        t = termino.lower()
        encontradas = [n for n in notas if t in n.titulo.lower() or t in n.contenido.lower()]
        
        if not encontradas:
            return [TextContent(type="text", text=f"🔍 Sin resultados para '{termino}'.")]
        
        texto = "\n\n".join([f"• {n.titulo}\n  ID: {n.id}" for n in encontradas])
        return [TextContent(type="text", text=f"🔍 Resultados para '{termino}':\n\n{texto}")]
    except Exception as e:
        logger.error(f"Error en buscar_notas: {e}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error interno al buscar notas: {str(e)}")]

@server.tool()
async def eliminar_nota(id: str = Field(..., description="ID de la nota a eliminar")) -> List[TextContent]:
    """Elimina una nota por su ID."""
    try:
        notas = cargar_notas()
        nuevas = [n for n in notas if n.id != id]
        
        if len(nuevas) == len(notas):
            return [TextContent(type="text", text=f"❌ No se encontró nota con ID: {id}")]
        
        guardar_notas(nuevas)
        return [TextContent(type="text", text=f"🗑️ Nota eliminada (ID: {id})")]
    except Exception as e:
        logger.error(f"Error en eliminar_nota: {e}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error interno al eliminar la nota: {str(e)}")]

async def main():
    logger.info("Iniciando servidor de notas con FastMCP...")
    # FastMCP se encarga automáticamente del bucle de lectura/escritura por STDIO
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())

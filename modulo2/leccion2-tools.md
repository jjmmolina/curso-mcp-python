# Lección 2.2: Implementando Tools (Herramientas)

## Introducción

Las **herramientas (tools)** son el corazón de un servidor MCP. Permiten que los modelos de IA ejecuten acciones específicas. En esta lección aprenderemos a crear herramientas robustas usando **FastMCP** y el **SDK base**.

## ⚠️ Regla Crítica de Logging

**NUNCA uses `print()` en servidores con transporte STDIO**. Esto corrompe la comunicación JSON-RPC.

```python
# ❌ MALO - Rompe el servidor STDIO
print("Processing request")

# ✅ BUENO - Usa logging
import logging
logger = logging.getLogger(__name__)
logger.info("Processing request")
```

## Tipos de Herramientas

### 1. Herramientas de Lectura (Read-only)
```python
@mcp.tool()
async def obtener_clima(ciudad: str) -> str:
    """Obtiene el clima actual de una ciudad."""
    # Solo lectura, sin efectos secundarios
    return f"Clima en {ciudad}: Soleado, 22°C"
```

### 2. Herramientas de Escritura (Write)
```python
@mcp.tool()
async def guardar_nota(titulo: str, contenido: str) -> str:
    """Guarda una nueva nota."""
    # Modifica datos
    await save_to_db(titulo, contenido)
    return "Nota guardada exitosamente"
```

### 3. Herramientas de Acción (Actions)
```python
@mcp.tool()
async def enviar_email(destinatario: str, asunto: str, mensaje: str) -> str:
    """Envía un email."""
    # Ejecuta una acción
    await send_email(destinatario, asunto, mensaje)
    return "Email enviado"
```

## Ejemplo Completo con FastMCP: Sistema de Notas

```python
# notas_server_fast.py
"""
Servidor MCP para gestión de notas usando FastMCP
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from mcp.server.fastmcp import FastMCP

# Configurar logging (NO usar print())
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Modelos de datos con Pydantic
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

# Crear servidor FastMCP
mcp = FastMCP("notas-mcp")

@mcp.tool()
async def crear_nota(
    titulo: str,
    contenido: str,
    etiquetas: Optional[List[str]] = None
) -> str:
    """Crea una nueva nota con título, contenido y etiquetas opcionales.
    
    Args:
        titulo: Título de la nota (máx. 100 caracteres)
        contenido: Contenido de la nota
        etiquetas: Lista opcional de etiquetas para organizar la nota
    """
    logger.info(f"Creando nota: {titulo}")
    
    # Cargar notas existentes
    notas = cargar_notas()
    
    # Crear nueva nota
    nueva_nota = Nota(
        id=f"nota_{datetime.now().timestamp()}",
        titulo=titulo[:100],  # Limitar longitud
        contenido=contenido,
        fecha_creacion=datetime.now().isoformat(),
        etiquetas=etiquetas or []
    )
    
    # Agregar y guardar
    notas.append(nueva_nota)
    guardar_notas(notas)
    
    return (
        f"✅ Nota creada exitosamente!\n\n"
        f"ID: {nueva_nota.id}\n"
        f"Título: {nueva_nota.titulo}\n"
        f"Etiquetas: {', '.join(nueva_nota.etiquetas) if nueva_nota.etiquetas else 'Ninguna'}"
    )

@mcp.tool()
async def listar_notas() -> str:
    """Lista todas las notas guardadas."""
    logger.info("Listando todas las notas")
    notas = cargar_notas()
    
    if not notas:
        return "📝 No hay notas guardadas."
    
    # Formatear lista de notas
    resultado = f"📝 Tienes {len(notas)} nota(s):\n\n"
    
    for nota in notas:
        etiquetas = f"[{', '.join(nota.etiquetas)}]" if nota.etiquetas else ""
        resultado += f"• {nota.titulo} {etiquetas}\n"
        resultado += f"  ID: {nota.id}\n"
        resultado += f"  Creada: {nota.fecha_creacion}\n"
        resultado += f"  {nota.contenido[:100]}{'...' if len(nota.contenido) > 100 else ''}\n\n"
    
    return resultado

@mcp.tool()
async def buscar_notas(termino: str) -> str:
    """Busca notas por término en título o contenido.
    
    Args:
        termino: Término a buscar en las notas
    """
    logger.info(f"Buscando notas con término: {termino}")
    notas = cargar_notas()
    
    termino_lower = termino.lower()
    
    # Buscar en título y contenido
    encontradas = [
        nota for nota in notas
        if termino_lower in nota.titulo.lower() or 
           termino_lower in nota.contenido.lower()
    ]
    
    if not encontradas:
        return f"🔍 No se encontraron notas con el término '{termino}'."
    
    resultado = f"🔍 Se encontraron {len(encontradas)} nota(s) con '{termino}':\n\n"
    
    for nota in encontradas:
        resultado += f"• {nota.titulo}\n"
        resultado += f"  ID: {nota.id}\n"
        resultado += f"  {nota.contenido[:150]}{'...' if len(nota.contenido) > 150 else ''}\n\n"
    
    return resultado

@mcp.tool()
async def eliminar_nota(id: str) -> str:
    """Elimina una nota por su ID.
    
    Args:
        id: ID de la nota a eliminar
    """
    logger.info(f"Eliminando nota: {id}")
    notas = cargar_notas()
    
    # Buscar y eliminar
    notas_filtradas = [nota for nota in notas if nota.id != id]
    
    if len(notas_filtradas) == len(notas):
        return f"❌ No se encontró una nota con ID: {id}"
    
    guardar_notas(notas_filtradas)
    
    return f"🗑️ Nota eliminada exitosamente (ID: {id})"

if __name__ == "__main__":
    logger.info("Iniciando servidor de notas MCP...")
    mcp.run(transport='stdio')
```

## Mejores Prácticas para Tools

### 1. Nombres de Tools (Siguiendo la Especificación)

Los nombres de herramientas deben seguir el formato especificado en la documentación oficial de MCP:

```python
# ✅ BUENO - Nombres claros y descriptivos
@mcp.tool()
async def calcular_impuesto(monto: float, tasa: float) -> str:
    """Calcula el impuesto sobre ventas para un monto dado."""
    ...

# ✅ BUENO - Usa snake_case
@mcp.tool()
async def convertir_moneda(cantidad: float, de: str, a: str) -> str:
    """Convierte una cantidad de una moneda a otra."""
    ...

# ❌ MALO - Nombres vagos o genéricos
@mcp.tool()
async def fn1(x: int) -> str:
    """hace algo"""
    ...
```

### 2. Descripciones Claras y Detalladas

El LLM usa las descripciones para decidir qué tool usar. Sé específico:

```python
# ✅ BUENO
@mcp.tool()
async def convertir_moneda(cantidad: float, de: str, a: str) -> str:
    """Convierte una cantidad de una moneda a otra usando tasas de cambio actuales.
    
    Soporta USD, EUR, GBP, JPY. Requiere conexión a internet para obtener
    tasas actualizadas.
    
    Args:
        cantidad: Cantidad a convertir (debe ser positiva)
        de: Código de moneda origen (USD, EUR, GBP, JPY)
        a: Código de moneda destino (USD, EUR, GBP, JPY)
    """
    ...

# ❌ MALO
@mcp.tool()
async def convertir_moneda(cantidad: float, de: str, a: str) -> str:
    """Convierte moneda."""
    ...
```

### 3. Validación con Type Hints y Pydantic

FastMCP usa type hints, pero puedes añadir validación adicional:

```python
from pydantic import Field, field_validator

@mcp.tool()
async def transferir_dinero(
    monto: float = Field(gt=0, description="Monto a transferir (debe ser positivo)"),
    origen: str = Field(pattern="^[0-9]{10}$", description="Cuenta origen (10 dígitos)"),
    destino: str = Field(pattern="^[0-9]{10}$", description="Cuenta destino (10 dígitos)")
) -> str:
    """Transfiere dinero entre cuentas bancarias."""
    if origen == destino:
        return "❌ Error: Las cuentas deben ser diferentes"
    
    # Lógica de transferencia
    return f"✅ Transferencia de ${monto} completada"
```

### 4. NUNCA usar print() en Servidores STDIO

```python
# ❌ MALO - Rompe el servidor STDIO
@mcp.tool()
async def procesar_datos(data: str) -> str:
    print(f"Processing {data}")  # ¡ESTO CORROMPE JSON-RPC!
    return "Done"

# ✅ BUENO - Usa logging
import logging
logger = logging.getLogger(__name__)

@mcp.tool()
async def procesar_datos(data: str) -> str:
    logger.info(f"Processing {data}")  # Escribe a stderr, no stdout
    return "Done"
```

### 5. Manejo de Errores Específico

```python
@mcp.tool()
async def dividir(a: float, b: float) -> str:
    """Divide dos números.
    
    Args:
        a: Dividendo
        b: Divisor (no puede ser cero)
    """
    if b == 0:
        return "❌ Error: No se puede dividir por cero"
    
    resultado = a / b
    return f"{a} ÷ {b} = {resultado}"
```

### 6. Respuestas Formateadas y Útiles

```python
# ✅ Usa emojis y formato claro para mejor UX
@mcp.tool()
async def calcular_total(subtotal: float, impuesto: float) -> str:
    """Calcula el total incluyendo impuestos."""
    total = subtotal * (1 + impuesto)
    impuesto_monto = subtotal * impuesto
    
    return (
        "✅ Cálculo completado!\n\n"
        "📊 Resultados:\n"
        f"   • Subtotal: ${subtotal:,.2f}\n"
        f"   • Impuesto ({impuesto*100}%): ${impuesto_monto:,.2f}\n"
        f"   • Total: ${total:,.2f}"
    )
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

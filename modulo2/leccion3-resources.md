# Lección 2.3: Trabajando con Resources (Recursos)

## ¿Qué son los Resources?

Los **recursos** son datos que el modelo puede leer pero no modificar directamente. Son perfectos para:
- Archivos de configuración
- Documentación
- Logs
- Datos de referencia
- Contenido estático

## Diferencia entre Tools y Resources

| Tools | Resources |
|-------|-----------|
| Ejecutan acciones | Proporcionan datos |
| Pueden modificar estado | Solo lectura |
| Requieren parámetros | Se acceden por URI |
| Responden con resultados | Responden con contenido |

## Estructura de un Resource

```python
from mcp.types import Resource

Resource(
    uri="schema://tipo/identificador",
    name="Nombre legible del recurso",
    description="Descripción de qué contiene",
    mimeType="text/plain"  # o application/json, etc.
)
```

## Ejemplo Completo: Sistema de Documentación

```python
# src/resources/docs_server.py
"""
Servidor MCP que expone documentación como recursos
"""

import asyncio
from pathlib import Path
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, McpError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("docs-mcp")

# Directorio de documentación
DOCS_DIR = Path("docs")
DOCS_DIR.mkdir(exist_ok=True)

@server.list_resources()
async def list_resources() -> List[Resource]:
    """Lista todos los recursos de documentación disponibles"""
    resources = []
    
    # Documentos estáticos
    resources.extend([
        Resource(
            uri="docs://guia/inicio",
            name="Guía de Inicio Rápido",
            description="Tutorial para comenzar con el sistema",
            mimeType="text/markdown"
        ),
        Resource(
            uri="docs://api/referencia",
            name="Referencia de API",
            description="Documentación completa de la API",
            mimeType="text/markdown"
        ),
        Resource(
            uri="docs://config/ejemplo",
            name="Configuración de Ejemplo",
            description="Archivo de configuración de ejemplo",
            mimeType="application/json"
        )
    ])
    
    # Documentos dinámicos desde el sistema de archivos
    if DOCS_DIR.exists():
        for archivo in DOCS_DIR.glob("*.md"):
            resources.append(Resource(
                uri=f"docs://file/{archivo.stem}",
                name=archivo.stem.replace("_", " ").title(),
                description=f"Documento: {archivo.name}",
                mimeType="text/markdown"
            ))
    
    logger.info(f"Listados {len(resources)} recursos")
    return resources

@server.read_resource()
async def read_resource(uri: str) -> List[TextContent]:
    """Lee el contenido de un recurso específico"""
    logger.info(f"Leyendo recurso: {uri}")
    
    try:
        # Recursos estáticos
        if uri == "docs://guia/inicio":
            contenido = """# Guía de Inicio Rápido

## Bienvenido

Esta es una guía rápida para comenzar a usar el sistema.

### Paso 1: Instalación

```bash
pip install mi-sistema
```

### Paso 2: Configuración

Crea un archivo `config.json`:

```json
{
    "nombre": "Mi Proyecto",
    "version": "1.0.0"
}
```

### Paso 3: Uso Básico

```python
from mi_sistema import App

app = App()
app.run()
```

## Próximos Pasos

- Lee la referencia de API
- Revisa los ejemplos
- Únete a la comunidad
"""
        
        elif uri == "docs://api/referencia":
            contenido = """# Referencia de API

## Clase App

### Métodos

#### `__init__(config: dict)`
Inicializa la aplicación con la configuración proporcionada.

**Parámetros:**
- `config` (dict): Diccionario con la configuración

#### `run()`
Ejecuta la aplicación principal.

**Retorna:**
- None

**Ejemplo:**
```python
app = App({"debug": True})
app.run()
```

## Funciones Utilitarias

### `cargar_config(ruta: str) -> dict`
Carga un archivo de configuración.

**Parámetros:**
- `ruta` (str): Ruta al archivo de configuración

**Retorna:**
- dict: Configuración cargada
"""
        
        elif uri == "docs://config/ejemplo":
            contenido = """{
    "app": {
        "nombre": "Mi Aplicación",
        "version": "1.0.0",
        "debug": false
    },
    "base_datos": {
        "host": "localhost",
        "puerto": 5432,
        "nombre": "mi_bd"
    },
    "logging": {
        "nivel": "INFO",
        "archivo": "app.log"
    }
}"""
        
        # Recursos del sistema de archivos
        elif uri.startswith("docs://file/"):
            nombre_archivo = uri.replace("docs://file/", "")
            ruta_archivo = DOCS_DIR / f"{nombre_archivo}.md"
            
            if not ruta_archivo.exists():
                raise McpError(
                    code=-32602,
                    message=f"Archivo no encontrado: {nombre_archivo}"
                )
            
            with open(ruta_archivo, 'r', encoding='utf-8') as f:
                contenido = f.read()
        
        else:
            raise McpError(
                code=-32602,
                message=f"Recurso no encontrado: {uri}"
            )
        
        return [TextContent(type="text", text=contenido)]
    
    except McpError:
        raise
    except Exception as e:
        logger.error(f"Error leyendo recurso {uri}: {e}", exc_info=True)
        raise McpError(
            code=-32603,
            message=f"Error leyendo recurso: {str(e)}"
        )

async def main():
    logger.info("Iniciando servidor de documentación MCP...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## URIs de Recursos

### Esquemas Comunes

```python
# Documentación
"docs://categoria/documento"

# Configuración
"config://app/settings"
"config://user/preferences"

# Datos
"data://database/schema"
"data://cache/statistics"

# Archivos
"file:///ruta/completa/archivo.txt"

# Custom
"myapp://logs/latest"
```

### Buenas Prácticas para URIs

```python
# ✅ Descriptivos y jerárquicos
"docs://manual/usuario/instalacion"
"config://database/production"

# ❌ Poco claros
"resource://1"
"data://x"
```

## Resources Dinámicos

### Basados en el Sistema de Archivos

```python
from pathlib import Path

@server.list_resources()
async def list_resources():
    resources = []
    
    # Listar todos los archivos .md en un directorio
    docs_path = Path("documentos")
    for archivo in docs_path.rglob("*.md"):
        # Crear URI relativa
        uri = f"docs://file/{archivo.relative_to(docs_path)}"
        
        resources.append(Resource(
            uri=uri,
            name=archivo.stem,
            description=f"Documento: {archivo.name}",
            mimeType="text/markdown"
        ))
    
    return resources
```

### Basados en Base de Datos

```python
import aiosqlite

@server.list_resources()
async def list_resources():
    resources = []
    
    async with aiosqlite.connect("app.db") as db:
        async with db.execute("SELECT id, titulo FROM articulos") as cursor:
            async for row in cursor:
                resources.append(Resource(
                    uri=f"db://articulos/{row[0]}",
                    name=row[1],
                    description=f"Artículo: {row[1]}",
                    mimeType="text/plain"
                ))
    
    return resources

@server.read_resource()
async def read_resource(uri: str):
    if uri.startswith("db://articulos/"):
        articulo_id = uri.split("/")[-1]
        
        async with aiosqlite.connect("app.db") as db:
            async with db.execute(
                "SELECT contenido FROM articulos WHERE id = ?",
                (articulo_id,)
            ) as cursor:
                row = await cursor.fetchone()
                
                if row:
                    return [TextContent(type="text", text=row[0])]
                else:
                    raise McpError(
                        code=-32602,
                        message=f"Artículo no encontrado: {articulo_id}"
                    )
```

## Diferentes Tipos de Contenido

### Text Content

```python
return [TextContent(
    type="text",
    text="Contenido del recurso..."
)]
```

### Image Content (Base64)

```python
import base64
from mcp.types import ImageContent

with open("imagen.png", "rb") as f:
    imagen_base64 = base64.b64encode(f.read()).decode()

return [ImageContent(
    type="image",
    data=imagen_base64,
    mimeType="image/png"
)]
```

### Embedded Resources

```python
from mcp.types import EmbeddedResource

return [EmbeddedResource(
    type="resource",
    resource=Resource(
        uri="nested://resource",
        name="Recurso Anidado",
        mimeType="text/plain"
    )
)]
```

## Ejemplo Avanzado: Sistema de Logs

```python
# src/resources/logs_server.py
"""
Servidor MCP para acceso a logs del sistema
"""

import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Resource, TextContent, McpError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("logs-mcp")

LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

@server.list_resources()
async def list_resources() -> List[Resource]:
    """Lista recursos de logs disponibles"""
    resources = []
    
    # Log más reciente
    resources.append(Resource(
        uri="logs://current",
        name="Log Actual",
        description="Últimas 100 líneas del log actual",
        mimeType="text/plain"
    ))
    
    # Logs por fecha
    if LOGS_DIR.exists():
        for log_file in sorted(LOGS_DIR.glob("*.log"), reverse=True):
            fecha = log_file.stem  # Asume formato YYYY-MM-DD.log
            
            resources.append(Resource(
                uri=f"logs://date/{fecha}",
                name=f"Log {fecha}",
                description=f"Log completo del {fecha}",
                mimeType="text/plain"
            ))
    
    # Resumen de errores
    resources.append(Resource(
        uri="logs://errors/summary",
        name="Resumen de Errores",
        description="Resumen de errores de los últimos 7 días",
        mimeType="text/markdown"
    ))
    
    return resources

@server.read_resource()
async def read_resource(uri: str) -> List[TextContent]:
    """Lee el contenido de un log específico"""
    
    try:
        if uri == "logs://current":
            # Leer últimas líneas del log actual
            log_actual = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
            
            if not log_actual.exists():
                return [TextContent(
                    type="text",
                    text="No hay log para hoy."
                )]
            
            with open(log_actual, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                ultimas_100 = lineas[-100:] if len(lineas) > 100 else lineas
                contenido = "".join(ultimas_100)
            
            return [TextContent(type="text", text=contenido)]
        
        elif uri.startswith("logs://date/"):
            fecha = uri.split("/")[-1]
            log_file = LOGS_DIR / f"{fecha}.log"
            
            if not log_file.exists():
                raise McpError(
                    code=-32602,
                    message=f"No existe log para la fecha: {fecha}"
                )
            
            with open(log_file, 'r', encoding='utf-8') as f:
                contenido = f.read()
            
            return [TextContent(type="text", text=contenido)]
        
        elif uri == "logs://errors/summary":
            # Generar resumen de errores
            resumen = await generar_resumen_errores()
            return [TextContent(type="text", text=resumen)]
        
        else:
            raise McpError(
                code=-32602,
                message=f"Recurso no encontrado: {uri}"
            )
    
    except McpError:
        raise
    except Exception as e:
        logger.error(f"Error leyendo log: {e}", exc_info=True)
        raise McpError(
            code=-32603,
            message=f"Error leyendo log: {str(e)}"
        )

async def generar_resumen_errores() -> str:
    """Genera un resumen de errores de los últimos días"""
    
    errores_por_dia = {}
    fecha_limite = datetime.now() - timedelta(days=7)
    
    for log_file in LOGS_DIR.glob("*.log"):
        try:
            fecha = datetime.strptime(log_file.stem, "%Y-%m-%d")
            
            if fecha < fecha_limite:
                continue
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lineas_error = [
                    linea for linea in f
                    if "ERROR" in linea or "CRITICAL" in linea
                ]
                
                if lineas_error:
                    errores_por_dia[log_file.stem] = len(lineas_error)
        
        except ValueError:
            continue
    
    # Formatear resumen
    resumen = "# Resumen de Errores (Últimos 7 días)\n\n"
    
    if not errores_por_dia:
        resumen += "✅ No se encontraron errores.\n"
    else:
        resumen += f"⚠️ Total de días con errores: {len(errores_por_dia)}\n\n"
        resumen += "## Errores por Día\n\n"
        
        for fecha in sorted(errores_por_dia.keys(), reverse=True):
            resumen += f"- **{fecha}**: {errores_por_dia[fecha]} errores\n"
    
    return resumen

async def main():
    logger.info("Iniciando servidor de logs MCP...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Recursos vs Tools: ¿Cuándo usar cada uno?

### Usa Resources cuando:
- ✅ El modelo necesita leer datos
- ✅ El contenido es relativamente estático
- ✅ No requiere parámetros complejos
- ✅ Quieres proporcionar documentación

### Usa Tools cuando:
- ✅ Necesitas ejecutar una acción
- ✅ Requiere lógica compleja
- ✅ Modifica estado
- ✅ Necesita validación de parámetros

## 📝 Ejercicios

### Ejercicio 1: Sistema de Configuración
Crea recursos para:
- Configuración de la aplicación
- Configuración de usuario
- Variables de entorno (sanitizadas)

### Ejercicio 2: Navegador de Archivos
Crea recursos que:
- Listen archivos en un directorio
- Permitan leer archivos de texto
- Muestren metadata (tamaño, fecha, etc.)

### Ejercicio 3: Monitor del Sistema
Crea recursos para:
- Estado actual del sistema (CPU, RAM)
- Procesos en ejecución
- Uso de disco

---

**Anterior:** [Lección 2.2 - Implementando Tools](leccion2-tools.md)  
**Siguiente:** [Módulo 3 - Características Avanzadas](../modulo3/leccion1-prompts.md)

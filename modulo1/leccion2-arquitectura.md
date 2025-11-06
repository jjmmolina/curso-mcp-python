# Lección 1.2: Arquitectura y Conceptos Clave

## Arquitectura de MCP

### Modelo Cliente-Servidor

MCP sigue un modelo cliente-servidor donde:

```
┌────────────────────────────────────────────┐
│           CLIENTE MCP                      │
│  (Claude Desktop, VS Code, etc.)           │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Motor de IA                     │     │
│  │  - Procesa instrucciones         │     │
│  │  - Decide usar tools/resources   │     │
│  └──────────────────────────────────┘     │
│                   │                        │
└───────────────────┼────────────────────────┘
                    │ JSON-RPC
                    ▼
┌────────────────────────────────────────────┐
│           SERVIDOR MCP                     │
│  (Tu implementación en Python)             │
│                                            │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
│  │  Tools   │  │Resources │  │ Prompts │ │
│  └──────────┘  └──────────┘  └─────────┘ │
└────────────────────────────────────────────┘
```

## Ciclo de Vida de una Solicitud

### 1. Inicialización

```python
# El cliente inicia la conexión
CLIENTE → SERVIDOR: initialize
SERVIDOR → CLIENTE: initialize_response (capacidades)
```

### 2. Descubrimiento

```python
# El cliente pregunta qué puede hacer el servidor
CLIENTE → SERVIDOR: tools/list
SERVIDOR → CLIENTE: [lista de tools disponibles]

CLIENTE → SERVIDOR: resources/list
SERVIDOR → CLIENTE: [lista de resources disponibles]
```

### 3. Ejecución

```python
# El modelo decide usar una herramienta
CLIENTE → SERVIDOR: tools/call {"name": "buscar", "arguments": {...}}
SERVIDOR → CLIENTE: [resultado de la ejecución]
```

## Componentes Detallados

### 1. Tools (Herramientas)

Las herramientas son funciones que el modelo puede ejecutar.

**Estructura de un Tool:**

```python
{
    "name": "nombre_herramienta",
    "description": "Qué hace la herramienta",
    "inputSchema": {
        "type": "object",
        "properties": {
            "parametro1": {
                "type": "string",
                "description": "Descripción del parámetro"
            }
        },
        "required": ["parametro1"]
    }
}
```

**Ejemplo Práctico:**

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

server = Server("calculadora")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="sumar",
            description="Suma dos números",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Primer número"},
                    "b": {"type": "number", "description": "Segundo número"}
                },
                "required": ["a", "b"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "sumar":
        resultado = arguments["a"] + arguments["b"]
        return [TextContent(
            type="text",
            text=f"El resultado es: {resultado}"
        )]
```

### 2. Resources (Recursos)

Los recursos son datos que el modelo puede leer.

**Estructura de un Resource:**

```python
{
    "uri": "recurso://tipo/identificador",
    "name": "Nombre del recurso",
    "description": "Qué contiene el recurso",
    "mimeType": "text/plain"  # u otro tipo MIME
}
```

**Ejemplo Práctico:**

```python
from mcp.types import Resource, TextContent

@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="config://app/settings",
            name="Configuración de la App",
            description="Configuración principal de la aplicación",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "config://app/settings":
        config = {
            "version": "1.0.0",
            "debug": False
        }
        return [TextContent(
            type="text",
            text=str(config)
        )]
```

### 3. Prompts

Los prompts son plantillas reutilizables para interacciones.

**Estructura de un Prompt:**

```python
{
    "name": "nombre_prompt",
    "description": "Para qué sirve este prompt",
    "arguments": [
        {
            "name": "parametro",
            "description": "Descripción",
            "required": True
        }
    ]
}
```

**Ejemplo Práctico:**

```python
from mcp.types import Prompt, PromptMessage

@server.list_prompts()
async def list_prompts():
    return [
        Prompt(
            name="analizar_codigo",
            description="Analiza código Python",
            arguments=[
                {
                    "name": "codigo",
                    "description": "El código a analizar",
                    "required": True
                }
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict):
    if name == "analizar_codigo":
        codigo = arguments["codigo"]
        return [
            PromptMessage(
                role="user",
                content=f"Analiza este código Python:\n\n{codigo}\n\nProvee:\n1. Resumen\n2. Mejoras posibles\n3. Errores potenciales"
            )
        ]
```

## Transporte y Comunicación

### JSON-RPC 2.0

MCP usa JSON-RPC para la comunicación:

```json
// Solicitud
{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "buscar",
        "arguments": {
            "query": "Python MCP"
        }
    }
}

// Respuesta
{
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "content": [
            {
                "type": "text",
                "text": "Resultados encontrados..."
            }
        ]
    }
}
```

### Tipos de Transporte

#### 1. STDIO (Standard Input/Output)
```python
# El más común para servidores locales
from mcp.server.stdio import stdio_server

async with stdio_server() as (read_stream, write_stream):
    await server.run(read_stream, write_stream)
```

#### 2. SSE (Server-Sent Events)
```python
# Para conexiones HTTP
from mcp.server.sse import sse_server
# Configuración HTTP...
```

## Manejo de Estado

### Servidor Sin Estado (Stateless)

Los servidores MCP son típicamente sin estado:

```python
# ❌ Evitar estado compartido
class BadServer:
    def __init__(self):
        self.contador = 0  # Problemático
    
    @server.call_tool()
    async def incrementar(self):
        self.contador += 1  # No persistente
```

### Persistencia Externa

```python
# ✅ Usar persistencia externa
import aiosqlite

@server.call_tool()
async def guardar_dato(name: str, arguments: dict):
    async with aiosqlite.connect("datos.db") as db:
        await db.execute(
            "INSERT INTO datos VALUES (?, ?)",
            (arguments["key"], arguments["value"])
        )
        await db.commit()
```

## Manejo de Errores

### Errores Estándar

```python
from mcp.types import McpError

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    try:
        # Tu lógica aquí
        pass
    except ValueError as e:
        raise McpError(
            code=-32602,  # Invalid params
            message=f"Parámetros inválidos: {e}"
        )
    except Exception as e:
        raise McpError(
            code=-32603,  # Internal error
            message=f"Error interno: {e}"
        )
```

## Seguridad y Permisos

### Principio de Mínimo Privilegio

```python
# Solo exponer lo necesario
@server.list_tools()
async def list_tools():
    return [
        # ✅ Específico y controlado
        Tool(
            name="leer_config_publica",
            description="Lee configuración pública"
        ),
        # ❌ Evitar acceso amplio
        # Tool(name="ejecutar_comando_sistema")
    ]
```

### Validación de Entrada

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    # Validar todos los argumentos
    if name == "leer_archivo":
        path = arguments.get("path")
        
        # ✅ Validar ruta
        if not path.startswith("/ruta/permitida/"):
            raise McpError(
                code=-32602,
                message="Ruta no permitida"
            )
```

## Mejores Prácticas

1. **Descripciones Claras**: El modelo usa las descripciones para decidir qué tool usar
2. **Validación Estricta**: Siempre valida entrada
3. **Errores Informativos**: Ayuda al modelo a entender qué salió mal
4. **Operaciones Atómicas**: Cada tool debe hacer una cosa bien
5. **Logging**: Registra todas las operaciones importantes

## 📝 Ejercicio

Diseña en papel un servidor MCP con:
1. 3 tools diferentes
2. 2 resources
3. 1 prompt

Define para cada uno:
- Nombre
- Descripción
- Parámetros/esquema

---

**Anterior:** [Lección 1.1 - Introducción](leccion1-introduccion.md)  
**Siguiente:** [Lección 1.3 - Configuración del Entorno](leccion3-configuracion.md)

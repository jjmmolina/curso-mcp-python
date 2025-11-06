# Lección 2.1: Tu Primer Servidor MCP

## Objetivo

Crear un servidor MCP funcional desde cero que exponga una herramienta simple.

## Servidor Básico: "Hola Mundo"

### Código Completo

```python
# src/hello_server.py
"""
Mi primer servidor MCP
Un servidor simple que puede saludar
"""

import asyncio
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Crear instancia del servidor
server = Server("hello-mcp")

# Definir qué herramientas están disponibles
@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    Lista todas las herramientas disponibles en este servidor.
    El cliente MCP llama a esto para descubrir qué puede hacer.
    """
    return [
        Tool(
            name="saludar",
            description="Saluda a una persona por su nombre",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "El nombre de la persona a saludar"
                    },
                    "formal": {
                        "type": "boolean",
                        "description": "Si el saludo debe ser formal o casual",
                        "default": False
                    }
                },
                "required": ["nombre"]
            }
        ),
        Tool(
            name="despedir",
            description="Se despide de una persona",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "El nombre de la persona"
                    }
                },
                "required": ["nombre"]
            }
        )
    ]

# Implementar la lógica de las herramientas
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """
    Ejecuta una herramienta específica con los argumentos proporcionados.
    """
    if name == "saludar":
        nombre = arguments["nombre"]
        formal = arguments.get("formal", False)
        
        if formal:
            mensaje = f"Buenos días, estimado/a {nombre}. Es un placer saludarle."
        else:
            mensaje = f"¡Hola {nombre}! ¿Cómo estás?"
        
        return [TextContent(
            type="text",
            text=mensaje
        )]
    
    elif name == "despedir":
        nombre = arguments["nombre"]
        mensaje = f"¡Hasta luego, {nombre}! Que tengas un excelente día."
        
        return [TextContent(
            type="text",
            text=mensaje
        )]
    
    else:
        raise ValueError(f"Herramienta desconocida: {name}")

# Punto de entrada del servidor
async def main():
    """
    Función principal que inicia el servidor MCP usando stdio.
    """
    # stdio_server maneja la comunicación a través de stdin/stdout
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    # Ejecutar el servidor
    asyncio.run(main())
```

## Análisis del Código

### 1. Importaciones

```python
import asyncio  # Para programación asíncrona
from mcp.server import Server  # Clase principal del servidor
from mcp.server.stdio import stdio_server  # Transporte stdio
from mcp.types import Tool, TextContent  # Tipos de datos MCP
```

### 2. Creación del Servidor

```python
server = Server("hello-mcp")
```

El nombre del servidor debe ser único y descriptivo.

### 3. Decorador @server.list_tools()

Este decorador registra la función que lista las herramientas disponibles:

```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [...]
```

**¿Cuándo se llama?**
- Cuando el cliente se conecta por primera vez
- Cuando el cliente necesita saber qué herramientas puede usar

### 4. Definición de Herramientas

```python
Tool(
    name="saludar",  # Nombre único
    description="Saluda a una persona por su nombre",  # Descripción clara
    inputSchema={  # JSON Schema para validación
        "type": "object",
        "properties": {
            "nombre": {
                "type": "string",
                "description": "El nombre de la persona a saludar"
            }
        },
        "required": ["nombre"]  # Parámetros obligatorios
    }
)
```

### 5. Decorador @server.call_tool()

Este decorador registra la función que ejecuta las herramientas:

```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "saludar":
        # Lógica de la herramienta
        return [TextContent(type="text", text=mensaje)]
```

### 6. Función Main

```python
async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
```

Esto inicia el servidor y lo mantiene escuchando por solicitudes.

## Ejecutar el Servidor

### Opción 1: Ejecución Directa (para testing)

```bash
python src/hello_server.py
```

El servidor quedará esperando entrada. Presiona Ctrl+C para detenerlo.

### Opción 2: Con Claude Desktop

1. Configurar `claude_desktop_config.json`:

```json
{
    "mcpServers": {
        "hello-server": {
            "command": "python",
            "args": [
                "C:\\ruta\\completa\\al\\proyecto\\src\\hello_server.py"
            ]
        }
    }
}
```

2. Reiniciar Claude Desktop

3. En Claude, puedes decir:
   - "Saluda a María de manera formal"
   - "Despídete de Juan"

## Mejorando el Servidor

### Agregar Logging

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info(f"Ejecutando herramienta: {name} con argumentos: {arguments}")
    
    if name == "saludar":
        # ... resto del código
        logger.info(f"Saludo generado: {mensaje}")
        return [TextContent(type="text", text=mensaje)]
```

### Agregar Validación

```python
from pydantic import BaseModel, validator

class SaludarArgs(BaseModel):
    nombre: str
    formal: bool = False
    
    @validator('nombre')
    def nombre_no_vacio(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip().title()

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "saludar":
        # Validar argumentos
        try:
            args = SaludarArgs(**arguments)
        except Exception as e:
            return [TextContent(
                type="text",
                text=f"Error en los argumentos: {str(e)}"
            )]
        
        # Usar args validados
        if args.formal:
            mensaje = f"Buenos días, estimado/a {args.nombre}."
        else:
            mensaje = f"¡Hola {args.nombre}!"
        
        return [TextContent(type="text", text=mensaje)]
```

### Manejo de Errores

```python
from mcp.types import McpError

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "saludar":
            nombre = arguments.get("nombre")
            
            if not nombre:
                raise McpError(
                    code=-32602,  # Invalid params
                    message="El parámetro 'nombre' es requerido"
                )
            
            # ... resto de la lógica
            
    except McpError:
        raise  # Re-lanzar errores MCP
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        raise McpError(
            code=-32603,  # Internal error
            message=f"Error interno del servidor: {str(e)}"
        )
```

## Versión Completa Mejorada

```python
# src/hello_server_v2.py
"""
Servidor MCP mejorado con logging, validación y manejo de errores
"""

import asyncio
import logging
from pydantic import BaseModel, validator
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, McpError

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hello_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Modelos de validación
class SaludarArgs(BaseModel):
    nombre: str
    formal: bool = False
    
    @validator('nombre')
    def nombre_valido(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        if len(v) > 50:
            raise ValueError('El nombre es demasiado largo')
        return v.strip().title()

class DespedirArgs(BaseModel):
    nombre: str
    
    @validator('nombre')
    def nombre_valido(cls, v):
        if not v.strip():
            raise ValueError('El nombre no puede estar vacío')
        return v.strip().title()

# Crear servidor
server = Server("hello-mcp-v2")

@server.list_tools()
async def list_tools() -> list[Tool]:
    logger.info("Cliente solicitó lista de herramientas")
    return [
        Tool(
            name="saludar",
            description="Saluda a una persona por su nombre de forma casual o formal",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre de la persona (máx. 50 caracteres)"
                    },
                    "formal": {
                        "type": "boolean",
                        "description": "True para saludo formal, False para casual",
                        "default": False
                    }
                },
                "required": ["nombre"]
            }
        ),
        Tool(
            name="despedir",
            description="Se despide de una persona de manera amigable",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Nombre de la persona"
                    }
                },
                "required": ["nombre"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    logger.info(f"Ejecutando: {name} con {arguments}")
    
    try:
        if name == "saludar":
            args = SaludarArgs(**arguments)
            
            if args.formal:
                mensaje = f"Buenos días, estimado/a {args.nombre}. Es un placer saludarle."
            else:
                mensaje = f"¡Hola {args.nombre}! ¿Cómo estás?"
            
            logger.info(f"Saludo generado para {args.nombre}")
            return [TextContent(type="text", text=mensaje)]
        
        elif name == "despedir":
            args = DespedirArgs(**arguments)
            mensaje = f"¡Hasta luego, {args.nombre}! Que tengas un excelente día."
            
            logger.info(f"Despedida generada para {args.nombre}")
            return [TextContent(type="text", text=mensaje)]
        
        else:
            raise McpError(
                code=-32601,  # Method not found
                message=f"Herramienta no encontrada: {name}"
            )
            
    except McpError:
        raise
    except ValueError as e:
        logger.warning(f"Argumentos inválidos: {e}")
        raise McpError(
            code=-32602,
            message=f"Argumentos inválidos: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        raise McpError(
            code=-32603,
            message="Error interno del servidor"
        )

async def main():
    logger.info("Iniciando servidor MCP...")
    async with stdio_server() as (read_stream, write_stream):
        logger.info("Servidor listo y esperando conexiones")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
```

## 📝 Ejercicios Prácticos

### Ejercicio 1: Calculadora Simple
Crea un servidor con herramientas para:
- Sumar dos números
- Restar dos números
- Multiplicar dos números
- Dividir dos números (con manejo de división por cero)

### Ejercicio 2: Conversor de Unidades
Crea herramientas para convertir:
- Celsius a Fahrenheit
- Kilómetros a millas
- Kilogramos a libras

### Ejercicio 3: Generador de Contraseñas
Crea una herramienta que genere contraseñas con opciones para:
- Longitud (8-32 caracteres)
- Incluir números (sí/no)
- Incluir símbolos (sí/no)
- Incluir mayúsculas (sí/no)

## Solución del Ejercicio 1

```python
# Ver: src/ejercicios/calculadora_server.py

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="sumar",
            description="Suma dos números",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        ),
        # ... más herramientas
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "sumar":
        resultado = arguments["a"] + arguments["b"]
        return [TextContent(
            type="text",
            text=f"{arguments['a']} + {arguments['b']} = {resultado}"
        )]
    # ... más implementaciones
```

---

**Anterior:** [Lección 1.3 - Configuración](../modulo1/leccion3-configuracion.md)  
**Siguiente:** [Lección 2.2 - Implementando Tools](leccion2-tools.md)

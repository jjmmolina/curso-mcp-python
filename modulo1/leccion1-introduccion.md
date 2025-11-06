# Lección 1.1: ¿Qué es MCP?

## Introducción

**Model Context Protocol (MCP)** es un protocolo abierto diseñado por Anthropic que permite que los modelos de IA (como Claude, GPT, etc.) se conecten de manera estandarizada con fuentes de datos y herramientas externas.

## ¿Por qué MCP?

Antes de MCP, cada aplicación de IA tenía que crear sus propias integraciones personalizadas. Esto resultaba en:

- ❌ Código duplicado
- ❌ Falta de estandarización
- ❌ Dificultad para mantener múltiples integraciones
- ❌ Barreras para compartir herramientas

### Con MCP obtenemos:

- ✅ **Protocolo estandarizado**: Una forma universal de comunicación
- ✅ **Reutilización**: Escribe una vez, usa en múltiples clientes
- ✅ **Seguridad**: Control sobre qué puede acceder el modelo
- ✅ **Escalabilidad**: Fácil de extender y mantener

## Conceptos Fundamentales

### Arquitectura MCP: Host, Cliente y Servidor

MCP sigue una arquitectura cliente-servidor con tres participantes clave:

#### 1. MCP Host (Aplicación de IA)
El **host** es la aplicación de IA que coordina todo (por ejemplo, Claude Desktop, VS Code). El host:
- Gestiona la interacción con el usuario
- Ejecuta el modelo de lenguaje (LLM)
- Crea y gestiona múltiples clientes MCP

#### 2. MCP Client (Componente de Conexión)
El **cliente** es un componente dentro del host que:
- Mantiene una conexión **uno-a-uno** con un servidor MCP
- Obtiene contexto del servidor para que el host lo use
- El host crea un cliente por cada servidor al que se conecta

#### 3. MCP Server (Tu Implementación)
El **servidor** es el programa que proporcionas y que:
- Expone capacidades (tools, resources, prompts)
- Puede ejecutarse localmente (STDIO) o remotamente (HTTP)
- Responde a las peticiones del cliente

### 3. Componentes Principales

#### 🔧 Tools (Herramientas)
Funciones que el modelo puede ejecutar:
- Leer/escribir archivos
- Consultar bases de datos
- Llamar APIs
- Realizar cálculos

#### 📦 Resources (Recursos)
Datos que el modelo puede leer:
- Archivos de configuración
- Contenido de bases de datos
- Documentación
- Logs del sistema

#### 💬 Prompts
Templates predefinidos para interacciones comunes:
- Plantillas de análisis
- Formatos de respuesta
- Workflows específicos

## Arquitectura Básica

```
┌─────────────────────────────────────────┐
│         MCP HOST                        │
│    (Claude Desktop, VS Code, etc.)      │
│                                         │
│  ┌─────────────┐    ┌─────────────┐   │
│  │ MCP Client  │    │ MCP Client  │   │
│  │     #1      │    │     #2      │   │
│  └──────┬──────┘    └──────┬──────┘   │
└─────────┼──────────────────┼──────────┘
          │                  │
          │ JSON-RPC        │ JSON-RPC
          ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│  MCP Server #1   │  │  MCP Server #2   │
│  (Tu código)     │  │  (Tu código)     │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         ▼                     ▼
   ┌──────────┐          ┌──────────┐
   │ Recursos │          │ Recursos │
   │ Locales  │          │   API    │
   └──────────┘          └──────────┘
```

**Relación 1:1**: Cada MCP Client mantiene una conexión dedicada con un MCP Server.

## Comunicación

MCP utiliza **JSON-RPC 2.0** sobre diferentes transportes:
- **stdio**: Entrada/Salida estándar (más común)
- **HTTP/SSE**: Server-Sent Events
- **WebSocket**: Para conexiones bidireccionales

## Casos de Uso

### 1. Acceso a Datos Privados
```python
# El modelo puede acceder a tus datos locales
# sin subirlos a la nube
servidor_documentos = MCPServer("documentos-empresa")
```

### 2. Automatización de Tareas
```python
# Crear tools para tareas repetitivas
@server.tool()
async def generar_reporte(fecha: str):
    # Genera reportes automáticamente
    pass
```

### 3. Integración con Sistemas
```python
# Conectar con APIs y servicios
@server.tool()
async def consultar_crm(cliente_id: str):
    # Accede a tu CRM
    pass
```

## Ventajas de MCP

1. **Privacidad**: Los datos se mantienen locales
2. **Flexibilidad**: Usa cualquier lenguaje (Python, TypeScript, etc.)
3. **Modular**: Combina múltiples servidores
4. **Open Source**: Comunidad activa y creciente

## Ejemplo Simple con FastMCP

MCP proporciona **FastMCP**, una interfaz simplificada que usa type hints y docstrings para definir herramientas automáticamente:

```python
from mcp.server.fastmcp import FastMCP

# Crear servidor con FastMCP
mcp = FastMCP("mi-primer-servidor")

# Definir una herramienta usando un decorador
@mcp.tool()
async def saludar(nombre: str) -> str:
    """Saluda a una persona por su nombre.
    
    Args:
        nombre: El nombre de la persona a saludar
    """
    return f"¡Hola, {nombre}!"

# Ejecutar el servidor
if __name__ == "__main__":
    mcp.run(transport='stdio')
```

**¿Qué hace FastMCP?**
- Lee los type hints para generar automáticamente el `inputSchema`
- Usa el docstring como `description` de la herramienta
- Simplifica el código eliminando boilerplate
- Perfecto para proyectos nuevos

### Ejemplo con el SDK Base (Más Control)

Si necesitas más control sobre la configuración:

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

# Crear servidor
server = Server("mi-primer-servidor")

# Definir herramientas manualmente
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="saludar",
            description="Saluda a una persona por su nombre",
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

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "saludar":
        nombre = arguments.get("nombre", "Mundo")
        return [TextContent(
            type="text",
            text=f"¡Hola, {nombre}!"
        )]
```

## Próximos Pasos

En la siguiente lección, profundizaremos en la arquitectura de MCP y cómo funcionan los componentes internamente.

## 📝 Ejercicio

**Reflexiona:**
1. ¿Qué herramientas te gustaría crear con MCP?
2. ¿Qué datos o recursos te gustaría que un modelo de IA pudiera acceder de forma segura?
3. ¿Qué problemas podrías resolver con MCP en tu trabajo diario?

---

**Siguiente:** [Lección 1.2 - Arquitectura y Conceptos Clave](leccion2-arquitectura.md)

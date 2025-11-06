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

### 1. Cliente MCP
El cliente es la aplicación que utiliza la IA (por ejemplo, Claude Desktop, VS Code con Copilot).

### 2. Servidor MCP
El servidor expone capacidades (tools, resources, prompts) que el cliente puede usar.

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
┌─────────────────┐         ┌──────────────────┐
│  Cliente MCP    │◄───────►│  Servidor MCP    │
│  (Claude, etc.) │  JSON-RPC│  (Tu código)     │
└─────────────────┘         └──────────────────┘
                                    │
                                    ▼
                            ┌──────────────────┐
                            │  Tus Recursos    │
                            │  - Archivos      │
                            │  - APIs          │
                            │  - Databases     │
                            └──────────────────┘
```

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

## Ejemplo Simple

```python
from mcp.server import Server
from mcp.types import Tool, TextContent

# Crear servidor
server = Server("mi-primer-servidor")

# Definir una herramienta
@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="saludar",
            description="Saluda a una persona",
            inputSchema={
                "type": "object",
                "properties": {
                    "nombre": {"type": "string"}
                }
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

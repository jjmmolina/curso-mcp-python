# Lección 1.2: Arquitectura y Conceptos Clave

## Arquitectura General de MCP

### Modelo Cliente-Servidor

MCP sigue un modelo cliente-servidor. La comunicación se realiza mediante el protocolo **JSON-RPC 2.0**, que permite al cliente invocar métodos en el servidor.

```
┌────────────────────────────────────────────┐
│           CLIENTE MCP                      │
│  (Claude Desktop, VS Code, etc.)           │
│                                            │
│  ┌──────────────────────────────────┐     │
│  │  Motor de IA (LLM)               │     │
│  │  - Procesa instrucciones del usuario   │     │
│  │  - Decide usar tools/resources         │     │
│  └──────────────────────────────────┘     │
│                   │                        │
└───────────────────┼────────────────────────┘
                    │ JSON-RPC (sobre STDIO, HTTP, etc.)
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

El **cliente** (como Claude) es responsable de gestionar la interacción con el usuario y el modelo de lenguaje (LLM). Cuando el LLM decide que necesita ejecutar una acción o leer datos, el cliente envía una solicitud JSON-RPC al **servidor**.

### Negociación de Capacidades (El Handshake `initialize`)

Antes de que un cliente pueda usar las herramientas o recursos de un servidor, debe ocurrir un "handshake" (apretón de manos) para establecer las reglas de comunicación. Este proceso se llama **negociación de capacidades** y se realiza a través del método `initialize`. Es el primer paso en el ciclo de vida de la comunicación.

1.  **El Cliente Inicia**: Tan pronto como el MCP Host (p. ej., VS Code) inicia tu servidor, el MCP Client envía una petición `initialize`. Esta petición informa al servidor sobre las capacidades del cliente.

    *Petición del Cliente:*
    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "method": "initialize",
      "params": {
        "processId": 12345,
        "clientInfo": {
          "name": "Visual Studio Code - Copilot",
          "version": "1.95.0"
        },
        "capabilities": {}
      }
    }
    ```

2.  **El Servidor Responde**: Tu servidor MCP debe responder con sus propias capacidades. Esto le dice al cliente qué versión del protocolo MCP habla y qué características opcionales soporta.

    *Respuesta del Servidor:*
    ```json
    {
      "jsonrpc": "2.0",
      "id": 1,
      "result": {
        "serverInfo": {
          "name": "mi-servidor-de-notas",
          "version": "1.0.0"
        },
        "capabilities": {
          "protocolVersion": "1.0",
          "workspace": {
            "reload": {
              "supported": true
            }
          }
        }
      }
    }
    ```

#### Capacidades Clave del Servidor

-   `protocolVersion`: **(Obligatorio)** La versión del protocolo MCP que implementa tu servidor. Actualmente, debe ser `"1.0"`.
-   `workspace/reload`: Una capacidad opcional que, si se establece en `true`, le dice al cliente que tu servidor puede recargar su configuración o estado si se le solicita. Esto es útil si, por ejemplo, tu servidor lee archivos de configuración y quieres que el cliente pueda pedirle que los vuelva a leer sin reiniciarse.

El SDK de `mcp` se encarga de esta respuesta por ti. `FastMCP` lo hace aún más sencillo:

```python
# Con FastMCP, la información del servidor se pasa en el constructor
server = FastMCP(
    name="mi-servidor-de-notas",
    description="Un servidor para gestionar notas.",
    version="1.0.0"
)

# El SDK generará automáticamente la respuesta `initialize` correcta.
```

## Arquitectura Interna del Servidor

Dentro de tu aplicación Python, el SDK de MCP (`mcp.server`) proporciona las abstracciones para manejar la comunicación y la lógica del servidor.

```
Petición JSON-RPC ("tools/call", ...)
        │
        ▼
┌──────────────────────────────────┐
│       Transporte (stdio/sse)     │
│  - Lee y escribe datos brutos    │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│      Motor del Servidor MCP      │
│  - Parsea JSON-RPC               │
│  - Valida la petición            │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│     Dispatcher (Despachador)     │
│  - Invoca el decorador correcto  │
└──────────────────────────────────┘
        │
        ├─► @server.call_tool()
        ├─► @server.read_resource()
        └─► @server.get_prompt()
        │
        ▼
┌──────────────────────────────────┐
│         Tu Lógica de Código      │
│  - Ejecuta la acción solicitada  │
└──────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────┐
│      Motor del Servidor MCP      │
│  - Serializa la respuesta a JSON │
└──────────────────────────────────┘
        │
        ▼
    Respuesta JSON-RPC
```

1.  **Transporte**: Es la capa de más bajo nivel. Se encarga de recibir y enviar los mensajes. `stdio_server` es un ejemplo que usa la entrada y salida estándar, ideal para servidores locales que se ejecutan como un subproceso.
2.  **Motor del Servidor**: El corazón del SDK. Parsea los mensajes JSON-RPC entrantes, valida que sigan el protocolo y prepara la respuesta.
3.  **Dispatcher**: Cuando llega una petición válida (p. ej., `method: "tools/call"`), el dispatcher busca la función que has registrado con el decorador correspondiente (`@server.call_tool`) y la invoca con los parámetros de la petición.
4.  **Tu Lógica**: Aquí es donde se ejecuta tu código. El resultado que devuelves es capturado por el motor del servidor.
5.  **Serialización**: El motor convierte tu respuesta (p. ej., una lista de `TextContent`) en una respuesta JSON-RPC válida y la envía de vuelta al cliente a través del transporte.

## Estructura de Ficheros y Carpetas

Para un proyecto escalable y mantenible, se recomienda la siguiente estructura:

```
mi_servidor_mcp/
├── .venv/                     # Entorno virtual de Python
├── src/
│   └── mi_servidor/           # Paquete principal de tu servidor
│       ├── __init__.py
│       ├── server.py          # Punto central: define el objeto `Server` y registra los handlers
│       ├── tools/             # Módulo para organizar las herramientas
│       │   ├── __init__.py
│       │   ├── notas.py       # Lógica para herramientas de notas
│       │   └── sistema.py     # Lógica para herramientas del sistema
│       ├── resources/         # Módulo para los recursos
│       │   ├── __init__.py
│       │   └── ficheros.py    # Lógica para exponer ficheros como recursos
│       ├── prompts/           # Módulo para los prompts
│       │   ├── __init__.py
│       │   └── analisis.py    # Lógica para prompts de análisis
│       └── models.py          # Modelos de datos Pydantic para validación
├── tests/                     # Tests para tu servidor
│   ├── __init__.py
│   ├── test_tools_notas.py
│   └── test_resources_ficheros.py
├── .env                       # Variables de entorno (API keys, etc.) - NO SUBIR A GIT
├── .gitignore                 # Ficheros a ignorar por git
├── README.md                  # Documentación del proyecto
└── requirements.txt           # Dependencias de Python
```

### ¿Por qué esta estructura?

-   **Separación de responsabilidades**: Cada componente (tools, resources, models) vive en su propio módulo, facilitando su mantenimiento.
-   **Escalabilidad**: Es fácil añadir nuevas herramientas o recursos creando nuevos ficheros en las carpetas correspondientes.
-   **Testing**: La lógica de negocio está separada de la definición del servidor, lo que facilita las pruebas unitarias.
-   **Reutilización**: Los modelos Pydantic definidos en `models.py` pueden ser reutilizados por diferentes herramientas.
-   **Punto de entrada claro**: El fichero `server.py` actúa como el compositor principal, importando y registrando la lógica de los otros módulos.

**Ejemplo de `server.py` en esta arquitectura:**

```python
# src/mi_servidor/server.py
from mcp.server import Server
from .tools import notas, sistema  # Importa la lógica de las herramientas
from .resources import ficheros

# 1. Crear la instancia del servidor
server = Server("mi-servidor-completo")

# 2. Registrar los handlers de cada módulo
# El SDK buscará los decoradores (@server.list_tools, etc.) en estos módulos
server.include_router(notas.router)
server.include_router(sistema.router)
server.include_router(ficheros.router)

# El punto de entrada (main.py o similar) importaría y ejecutaría este servidor.
```

## Ciclo de Vida de una Solicitud

### 1. Inicialización y Negociación
El cliente se conecta y pregunta al servidor qué capacidades tiene. Este es el handshake.

```
CLIENTE → SERVIDOR: initialize
SERVIDOR → CLIENTE: initialize_response (con las capacidades del servidor)
```
Tras una inicialización exitosa, el cliente envía una notificación `initialized`.

```
CLIENTE → SERVIDOR: initialized
```

### 2. Descubrimiento
El cliente pide la lista de todos los componentes disponibles que el servidor ha expuesto.

```
CLIENTE → SERVIDOR: tools/list
SERVIDOR → CLIENTE: [lista de todos los tools]

CLIENTE → SERVIDOR: resources/list
SERVIDOR → CLIENTE: [lista de todos los resources]
```

### 3. Ejecución
El LLM, basándose en la conversación y la lista de componentes, decide usar uno.

```python
# El modelo decide usar una herramienta
CLIENTE → SERVIDOR: tools/call {"name": "crear_nota", "arguments": {...}}

# El servidor ejecuta la lógica asociada y devuelve el resultado
SERVIDOR → CLIENTE: [resultado de la ejecución]
```

## Componentes Detallados

### 1. Tools (Herramientas)
Funciones que el modelo puede ejecutar para realizar acciones.

**Estructura de un Tool:**
-   `name`: Nombre único.
-   `description`: Explicación clara de lo que hace. **Es lo más importante**, ya que el LLM lo usa para decidir si usar la herramienta.
-   `inputSchema`: Un [Esquema JSON](https://json-schema.org/) que define los parámetros. El servidor lo usa para validar la entrada automáticamente antes de llamar a tu función.

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
            description="Suma dos números y devuelve el resultado.",
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
        return [TextContent(type="text", text=f"El resultado es: {resultado}")]
```

### 2. Resources (Recursos)
Datos que el modelo puede leer para obtener contexto. Son de solo lectura.

**Estructura de un Resource:**
-   `uri`: Identificador único del recurso (p. ej., `file://documento.txt`).
-   `name`: Nombre legible.
-   `description`: Explicación del contenido.
-   `mimeType`: Formato del contenido (p. ej., `text/plain`, `application/json`).

**Ejemplo Práctico:**
```python
from mcp.types import Resource, TextContent

@server.list_resources()
async def list_resources():
    return [
        Resource(
            uri="config://app/settings",
            name="Configuración de la App",
            description="Muestra la configuración principal de la aplicación.",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def read_resource(uri: str):
    if uri == "config://app/settings":
        config = {"version": "1.0.0", "debug": False}
        return [TextContent(type="text", text=str(config))]
```

### 3. Prompts
Plantillas reutilizables que guían al LLM para realizar tareas complejas o estandarizadas.

**Ejemplo Práctico:**
```python
from mcp.types import Prompt, PromptMessage, GetPromptResult

@server.list_prompts()
async def list_prompts():
    return [
        Prompt(
            name="analizar_codigo",
            description="Genera un prompt para analizar código Python en busca de mejoras.",
            arguments=[{"name": "codigo", "description": "El código a analizar", "required": True}]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "analizar_codigo":
        codigo = arguments["codigo"]
        mensaje = f"Analiza este código Python:\n\n{codigo}\n\nProvee:\n1. Resumen\n2. Mejoras posibles\n3. Errores potenciales"
        return GetPromptResult(
            messages=[PromptMessage(role="user", content=TextContent(type="text", text=mensaje))]
        )
```

## Transporte y Comunicación

### JSON-RPC 2.0
MCP usa este protocolo estándar para la comunicación. Una petición especifica un `method` (p. ej., `tools/call`) y `params`, y el servidor devuelve un `result` o un `error`.

### Tipos de Transporte
-   **STDIO (Standard Input/Output)**: Ideal para servidores locales. El cliente (p. ej., Claude Desktop) ejecuta tu script de Python como un subproceso y se comunica a través de la entrada/salida estándar.
-   **SSE (Server-Sent Events)**: Útil para comunicación web. Permite al servidor enviar actualizaciones al cliente sobre una conexión HTTP.

## Manejo de Estado y Seguridad

-   **Sin Estado (Stateless)**: Los servidores MCP deben ser, idealmente, sin estado. La persistencia debe delegarse a una base de datos, un sistema de ficheros o una API externa.
-   **Validación de Entrada**: Nunca confíes en los datos del cliente. Usa `inputSchema` y modelos Pydantic para validar todo.
-   **Mínimo Privilegio**: Solo expón las herramientas y recursos estrictamente necesarios. Evita herramientas que puedan ejecutar comandos arbitrarios o acceder a rutas de ficheros no controladas.

## 📝 Ejercicio

Basado en la nueva estructura de ficheros propuesta:
1.  Dibuja en papel cómo organizarías un servidor para una **biblioteca musical**.
2.  ¿En qué fichero iría la tool `buscar_cancion(titulo: str)`?
3.  ¿Dónde definirías el modelo Pydantic `Cancion`?
4.  ¿Cómo expondrías la letra de una canción como un `Resource`?

---

**Anterior:** [Lección 1.1 - Introducción](leccion1-introduccion.md)  
**Siguiente:** [Lección 1.3 - Configuración del Entorno](leccion3-configuracion.md)


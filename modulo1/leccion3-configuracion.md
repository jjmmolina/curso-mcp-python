# Lección 1.3: Configuración del Entorno

## Requisitos del Sistema

### Python
- **Versión mínima**: Python 3.10
- **Versión recomendada**: Python 3.11 o 3.12

Verifica tu versión:
```bash
python --version
```

### Sistema Operativo
- Windows 10/11
- macOS 10.15+
- Linux (Ubuntu 20.04+, etc.)

## Instalación Paso a Paso

MCP recomienda usar **`uv`**, un gestor de paquetes moderno y rápido para Python, aunque también puedes usar `pip` tradicional.

### Opción 1: Usar `uv` (Recomendado)

`uv` es significativamente más rápido que pip y simplifica la gestión de entornos.

#### Windows (PowerShell)
```powershell
# Instalar uv
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Reiniciar el terminal para que uv esté disponible

# Crear proyecto
uv init mi-servidor-mcp
cd mi-servidor-mcp

# Crear entorno virtual
uv venv

# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Instalar MCP con CLI
uv add "mcp[cli]"
```

#### Linux/macOS
```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reiniciar el terminal

# Crear proyecto
uv init mi-servidor-mcp
cd mi-servidor-mcp

# Crear entorno virtual y activarlo
uv venv
source .venv/bin/activate

# Instalar MCP con CLI
uv add "mcp[cli]"
```

### Opción 2: Usar pip (Tradicional)

#### Windows (PowerShell)
```powershell
# Navegar a tu carpeta de proyectos
cd C:\mis-proyectos

# Crear el directorio del proyecto
mkdir mi-servidor-mcp
cd mi-servidor-mcp

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
.venv\Scripts\Activate.ps1

# Si hay error de permisos, ejecutar:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Instalar MCP
pip install "mcp[cli]"
```

#### Linux/macOS
```bash
# Navegar a tu carpeta de proyectos
cd ~/proyectos

# Crear el directorio del proyecto
mkdir mi-servidor-mcp
cd mi-servidor-mcp

# Crear entorno virtual
python3 -m venv .venv

# Activar entorno virtual
source .venv/bin/activate

# Instalar MCP
pip install "mcp[cli]"
```

### Verificar Instalación

```bash
# Con uv
uv pip show mcp

# Con pip
pip show mcp
```

**requirements.txt completo:**
```txt
# MCP Core (versión mínima 1.2.0 para FastMCP)
mcp[cli]>=1.2.0

# Async y utilidades
aiofiles>=23.2.1
python-dotenv>=1.0.0

# HTTP (para APIs)
httpx>=0.25.0

# Validación de datos
pydantic>=2.5.0
typing-extensions>=4.8.0

# Base de datos (opcional)
sqlalchemy>=2.0.0
aiosqlite>=0.19.0

# Seguridad (opcional)
bleach>=6.0.0
cryptography>=41.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0

# Linting
ruff>=0.1.0
```

### Instalar Dependencias

```bash
# Con uv (recomendado)
uv pip install -r requirements.txt

# Con pip
pip install -r requirements.txt
```

## ⚠️ Advertencia Crítica sobre Logging en Servidores STDIO

**NUNCA escribas a stdout (salida estándar) en servidores que usen transporte STDIO.** Esto corromperá los mensajes JSON-RPC y romperá tu servidor.

### ❌ **MALO** (Corrompe el servidor STDIO)
```python
# Estos comandos NO DEBEN USARSE en servidores STDIO:
print("Processing request")           # ❌ Python
console.log("Processing request")     # ❌ JavaScript
fmt.Println("Processing request")     # ❌ Go
System.out.println("...")             # ❌ Java
```

### ✅ **BUENO** (Escribe a stderr o archivos)
```python
import logging

# Configurar logging para escribir a stderr (no stdout)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Por defecto usa stderr, ¡NO stdout!
    ]
)

logger = logging.getLogger(__name__)

# Ahora puedes usar logging de forma segura
logger.info("Processing request")
logger.error("Something went wrong")
logger.debug("Debug info")
```

### Para Servidores HTTP/SSE

Si usas transporte HTTP en lugar de STDIO, **SÍ puedes usar** `print()` sin problemas, ya que no interfiere con las respuestas HTTP.

**Regla de oro**: Si tu servidor usa `stdio_server()`, NUNCA uses `print()`. Usa siempre `logging`.

## Configuración de Editores

### Visual Studio Code (Recomendado)

#### 1. Instalar VS Code
Descarga desde: https://code.visualstudio.com/

#### 2. Extensiones Recomendadas

```json
// .vscode/extensions.json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "ms-python.black-formatter",
        "GitHub.copilot"
    ]
}
```

#### 3. Configuración del Workspace

```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "${workspaceFolder}/venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "editor.formatOnSave": true,
    "python.analysis.typeCheckingMode": "basic"
}
```

#### 4. Tareas de VS Code

```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Run MCP Server",
            "type": "shell",
            "command": "${workspaceFolder}/venv/bin/python",
            "args": [
                "-m",
                "mcp.server.stdio",
                "${file}"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            }
        }
    ]
}
```

### PyCharm

1. Abrir proyecto
2. File → Settings → Project → Python Interpreter
3. Agregar nuevo intérprete → Existing environment
4. Seleccionar `venv/bin/python`

## Configuración de Cliente MCP (Claude Desktop)

### Instalación de Claude Desktop

1. Descargar desde: https://claude.ai/download
2. Instalar la aplicación

### Configurar tu Servidor MCP

#### Windows
Ubicación del archivo de configuración:
```
%APPDATA%\Claude\claude_desktop_config.json
```

#### macOS
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

#### Linux
```
~/.config/Claude/claude_desktop_config.json
```

### Ejemplo de Configuración

```json
{
    "mcpServers": {
        "mi-servidor": {
            "command": "python",
            "args": [
                "-m",
                "mcp.server.stdio",
                "C:\\ruta\\a\\tu\\servidor.py"
            ],
            "env": {
                "PYTHONPATH": "C:\\ruta\\a\\tu\\proyecto"
            }
        }
    }
}
```

### Ejemplo para Linux/macOS

```json
{
    "mcpServers": {
        "mi-servidor": {
            "command": "python3",
            "args": [
                "-m",
                "mcp.server.stdio",
                "/ruta/a/tu/servidor.py"
            ],
            "env": {
                "PYTHONPATH": "/ruta/a/tu/proyecto"
            }
        }
    }
}
```

## Estructura de Proyecto Recomendada

```
curso-mcp/
│
├── venv/                    # Entorno virtual
│
├── src/                     # Código fuente
│   ├── __init__.py
│   ├── server.py           # Servidor principal
│   ├── tools/              # Herramientas
│   │   ├── __init__.py
│   │   └── calculadora.py
│   ├── resources/          # Recursos
│   │   ├── __init__.py
│   │   └── archivos.py
│   └── prompts/            # Prompts
│       ├── __init__.py
│       └── templates.py
│
├── tests/                   # Tests
│   ├── __init__.py
│   ├── test_server.py
│   └── test_tools.py
│
├── data/                    # Datos (opcional)
│   └── ejemplo.json
│
├── .env                     # Variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

## Crear la Estructura

```bash
# Crear directorios
mkdir -p src/tools src/resources src/prompts tests data

# Crear archivos __init__.py
touch src/__init__.py
touch src/tools/__init__.py
touch src/resources/__init__.py
touch src/prompts/__init__.py
touch tests/__init__.py

# Crear archivos principales
touch src/server.py
touch .env
touch .gitignore
```

## Archivo .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# MCP
*.log

# Datos sensibles
.env
*.db
*.sqlite

# OS
.DS_Store
Thumbs.db
```

## Archivo .env de Ejemplo

```bash
# .env
DEBUG=True
LOG_LEVEL=INFO

# Si usas APIs externas
API_KEY=tu_api_key_aqui
```

## Verificación de Instalación

### Opción 1: Servidor Simple con FastMCP (Recomendado)

```python
# test_install.py
from mcp.server.fastmcp import FastMCP
import logging

# Configurar logging (NO USAR print() en servidores STDIO)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear servidor
mcp = FastMCP("test-server")

@mcp.tool()
async def test() -> str:
    """Herramienta de prueba para verificar la instalación."""
    logger.info("Tool 'test' ejecutada correctamente")
    return "✅ Instalación correcta con FastMCP!"

if __name__ == "__main__":
    logger.info("Iniciando servidor de prueba...")
    mcp.run(transport='stdio')
```

### Opción 2: Servidor con SDK Base

```python
# test_install_base.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("test-server")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name="test",
            description="Herramienta de prueba",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    logger.info(f"Ejecutando tool: {name}")
    return [TextContent(type="text", text="✅ Instalación correcta con SDK base!")]

if __name__ == "__main__":
    import asyncio
    from mcp.server.stdio import stdio_server
    
    async def main():
        logger.info("Iniciando servidor de prueba...")
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    
    asyncio.run(main())
```

### Ejecutar el test

```bash
# Con uv
uv run test_install.py

# Con Python directo
python test_install.py
```

Si todo está bien configurado, deberías ver en **stderr** (no stdout):
```
INFO:__main__:Iniciando servidor de prueba...
```

Y el servidor esperará mensajes JSON-RPC en stdin.

## Solución de Problemas Comunes

### Error: "No module named 'mcp'"

```bash
# Asegúrate de que el entorno virtual está activado
# Windows
.\venv\Scripts\Activate.ps1

# Linux/macOS
source venv/bin/activate

# Reinstala MCP
pip install --upgrade mcp
```

### Error: "Python version too old"

```bash
# Verifica tu versión
python --version

# Necesitas Python 3.10+
# Descarga desde python.org
```

### Error en Claude Desktop

1. Verifica la ruta en `claude_desktop_config.json`
2. Usa rutas absolutas
3. Reinicia Claude Desktop
4. Revisa los logs en:
   - Windows: `%APPDATA%\Claude\logs`
   - macOS: `~/Library/Logs/Claude`

## 📝 Checklist de Configuración

- [ ] Python 3.10+ instalado
- [ ] Entorno virtual creado y activado
- [ ] MCP SDK instalado
- [ ] VS Code configurado (opcional)
- [ ] Estructura de proyecto creada
- [ ] Claude Desktop instalado (para testing)
- [ ] Servidor de prueba ejecutado exitosamente

## Próximos Pasos

¡Ya tienes todo configurado! En el próximo módulo crearemos nuestro primer servidor MCP funcional.

---

**Anterior:** [Lección 1.2 - Arquitectura](leccion2-arquitectura.md)  
**Siguiente:** [Módulo 2 - Primeros Pasos](../modulo2/leccion1-primer-servidor.md)

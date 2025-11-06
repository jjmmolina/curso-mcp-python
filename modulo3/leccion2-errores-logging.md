# Lección 3.2: Manejo de Errores y Logging

## Introducción

El manejo adecuado de errores y el logging son fundamentales para crear servidores MCP robustos y mantenibles. En esta lección aprenderemos las mejores prácticas para gestionar errores y registrar eventos.

## Tipos de Errores en MCP

### 1. Errores de Protocolo MCP

```python
from mcp.types import McpError

# Error de método no encontrado
McpError(code=-32601, message="Método no encontrado")

# Error de parámetros inválidos
McpError(code=-32602, message="Parámetros inválidos")

# Error interno del servidor
McpError(code=-32603, message="Error interno del servidor")

# Error de aplicación
McpError(code=-32000, message="Error personalizado")
```

### 2. Códigos de Error Estándar JSON-RPC

```python
PARSE_ERROR = -32700        # Error al parsear JSON
INVALID_REQUEST = -32600    # Request JSON inválido
METHOD_NOT_FOUND = -32601   # Método no existe
INVALID_PARAMS = -32602     # Parámetros inválidos
INTERNAL_ERROR = -32603     # Error interno del servidor
SERVER_ERROR = -32000       # Errores personalizados (-32000 a -32099)
```

## Manejo de Errores Robusto

### Ejemplo Completo

```python
# src/error_handling/robust_server.py
"""
Servidor MCP con manejo robusto de errores
"""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, Field, validator, ValidationError
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, McpError

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Errores personalizados
class ServerError(Exception):
    """Error base del servidor"""
    pass

class ValidationError(ServerError):
    """Error de validación de datos"""
    pass

class StorageError(ServerError):
    """Error de almacenamiento"""
    pass

class NotFoundError(ServerError):
    """Recurso no encontrado"""
    pass

# Modelos de datos
class Tarea(BaseModel):
    id: str
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: str = ""
    prioridad: str = Field(default="media")
    completada: bool = False
    fecha_creacion: str
    
    @validator('prioridad')
    def validar_prioridad(cls, v):
        prioridades_validas = ['baja', 'media', 'alta']
        if v.lower() not in prioridades_validas:
            raise ValueError(
                f"Prioridad '{v}' no válida. "
                f"Use: {', '.join(prioridades_validas)}"
            )
        return v.lower()

class CrearTareaArgs(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    descripcion: Optional[str] = ""
    prioridad: Optional[str] = "media"
    
    @validator('prioridad')
    def validar_prioridad(cls, v):
        if v is None:
            return "media"
        prioridades_validas = ['baja', 'media', 'alta']
        if v.lower() not in prioridades_validas:
            raise ValueError(
                f"Prioridad '{v}' no válida. "
                f"Use: {', '.join(prioridades_validas)}"
            )
        return v.lower()

# Almacenamiento simulado
class TareaStorage:
    """Maneja el almacenamiento de tareas con manejo de errores"""
    
    def __init__(self, archivo: Path):
        self.archivo = archivo
        self._asegurar_archivo()
    
    def _asegurar_archivo(self):
        """Asegura que el archivo de almacenamiento existe"""
        try:
            self.archivo.parent.mkdir(parents=True, exist_ok=True)
            if not self.archivo.exists():
                self.archivo.write_text('[]', encoding='utf-8')
                logger.info(f"Archivo de almacenamiento creado: {self.archivo}")
        except Exception as e:
            logger.error(f"Error creando archivo de almacenamiento: {e}")
            raise StorageError(f"No se pudo crear el almacenamiento: {e}")
    
    def cargar(self) -> List[Tarea]:
        """Carga tareas con manejo de errores"""
        try:
            import json
            with open(self.archivo, 'r', encoding='utf-8') as f:
                data = json.load(f)
                tareas = [Tarea(**t) for t in data]
                logger.debug(f"Cargadas {len(tareas)} tareas")
                return tareas
        except json.JSONDecodeError as e:
            logger.error(f"Error JSON al cargar tareas: {e}")
            raise StorageError(f"Archivo corrupto: {e}")
        except ValidationError as e:
            logger.error(f"Error de validación al cargar tareas: {e}")
            raise StorageError(f"Datos inválidos en almacenamiento: {e}")
        except Exception as e:
            logger.error(f"Error inesperado cargando tareas: {e}")
            raise StorageError(f"Error al cargar tareas: {e}")
    
    def guardar(self, tareas: List[Tarea]):
        """Guarda tareas con manejo de errores"""
        try:
            import json
            with open(self.archivo, 'w', encoding='utf-8') as f:
                data = [t.dict() for t in tareas]
                json.dump(data, f, ensure_ascii=False, indent=2)
                logger.debug(f"Guardadas {len(tareas)} tareas")
        except Exception as e:
            logger.error(f"Error guardando tareas: {e}")
            raise StorageError(f"No se pudieron guardar las tareas: {e}")

# Servidor
server = Server("tareas-robustas-mcp")
storage = TareaStorage(Path("data/tareas.json"))

@server.list_tools()
async def list_tools() -> List[Tool]:
    """Lista las herramientas disponibles"""
    return [
        Tool(
            name="crear_tarea",
            description="Crea una nueva tarea con título, descripción y prioridad",
            inputSchema={
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "Título de la tarea (1-200 caracteres)",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "descripcion": {
                        "type": "string",
                        "description": "Descripción detallada de la tarea",
                        "default": ""
                    },
                    "prioridad": {
                        "type": "string",
                        "description": "Prioridad: baja, media, alta",
                        "enum": ["baja", "media", "alta"],
                        "default": "media"
                    }
                },
                "required": ["titulo"]
            }
        ),
        Tool(
            name="listar_tareas",
            description="Lista todas las tareas con filtros opcionales",
            inputSchema={
                "type": "object",
                "properties": {
                    "prioridad": {
                        "type": "string",
                        "description": "Filtrar por prioridad",
                        "enum": ["baja", "media", "alta"]
                    },
                    "completada": {
                        "type": "boolean",
                        "description": "Filtrar por estado de completitud"
                    }
                }
            }
        ),
        Tool(
            name="completar_tarea",
            description="Marca una tarea como completada",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "ID de la tarea"
                    }
                },
                "required": ["id"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Ejecuta herramientas con manejo robusto de errores"""
    
    logger.info(f"Ejecutando herramienta: {name}")
    logger.debug(f"Argumentos: {arguments}")
    
    try:
        if name == "crear_tarea":
            return await crear_tarea(arguments)
        elif name == "listar_tareas":
            return await listar_tareas(arguments)
        elif name == "completar_tarea":
            return await completar_tarea(arguments)
        else:
            logger.warning(f"Herramienta no encontrada: {name}")
            raise McpError(
                code=-32601,
                message=f"Herramienta '{name}' no existe"
            )
    
    except McpError:
        # Re-lanzar errores MCP tal cual
        raise
    
    except ValidationError as e:
        logger.error(f"Error de validación en {name}: {e}")
        raise McpError(
            code=-32602,
            message=f"Parámetros inválidos: {str(e)}"
        )
    
    except NotFoundError as e:
        logger.warning(f"Recurso no encontrado en {name}: {e}")
        raise McpError(
            code=-32000,
            message=str(e)
        )
    
    except StorageError as e:
        logger.error(f"Error de almacenamiento en {name}: {e}")
        raise McpError(
            code=-32603,
            message=f"Error interno: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Error inesperado en {name}: {e}", exc_info=True)
        raise McpError(
            code=-32603,
            message="Error interno del servidor. Por favor, contacte al administrador."
        )

async def crear_tarea(arguments: dict) -> List[TextContent]:
    """Crea una nueva tarea"""
    try:
        # Validar argumentos
        args = CrearTareaArgs(**arguments)
        
        # Cargar tareas existentes
        tareas = storage.cargar()
        
        # Crear nueva tarea
        nueva_tarea = Tarea(
            id=f"tarea_{datetime.now().timestamp()}",
            titulo=args.titulo,
            descripcion=args.descripcion or "",
            prioridad=args.prioridad,
            completada=False,
            fecha_creacion=datetime.now().isoformat()
        )
        
        # Guardar
        tareas.append(nueva_tarea)
        storage.guardar(tareas)
        
        logger.info(f"Tarea creada: {nueva_tarea.id} - {nueva_tarea.titulo}")
        
        return [TextContent(
            type="text",
            text=f"✅ Tarea creada exitosamente!\n\n"
                 f"📝 **{nueva_tarea.titulo}**\n"
                 f"ID: {nueva_tarea.id}\n"
                 f"Prioridad: {nueva_tarea.prioridad.upper()}\n"
                 f"Descripción: {nueva_tarea.descripcion or '(sin descripción)'}"
        )]
    
    except ValidationError as e:
        logger.error(f"Error de validación: {e}")
        raise

async def listar_tareas(arguments: dict) -> List[TextContent]:
    """Lista tareas con filtros opcionales"""
    tareas = storage.cargar()
    
    # Aplicar filtros
    prioridad_filtro = arguments.get("prioridad")
    completada_filtro = arguments.get("completada")
    
    if prioridad_filtro:
        tareas = [t for t in tareas if t.prioridad == prioridad_filtro.lower()]
    
    if completada_filtro is not None:
        tareas = [t for t in tareas if t.completada == completada_filtro]
    
    if not tareas:
        return [TextContent(
            type="text",
            text="📋 No hay tareas que coincidan con los filtros."
        )]
    
    # Formatear salida
    resultado = f"📋 **{len(tareas)} tarea(s) encontrada(s)**\n\n"
    
    for tarea in tareas:
        estado = "✅" if tarea.completada else "⬜"
        resultado += f"{estado} **{tarea.titulo}**\n"
        resultado += f"   ID: {tarea.id}\n"
        resultado += f"   Prioridad: {tarea.prioridad.upper()}\n"
        if tarea.descripcion:
            resultado += f"   {tarea.descripcion[:100]}{'...' if len(tarea.descripcion) > 100 else ''}\n"
        resultado += "\n"
    
    logger.info(f"Listadas {len(tareas)} tareas")
    return [TextContent(type="text", text=resultado)]

async def completar_tarea(arguments: dict) -> List[TextContent]:
    """Marca una tarea como completada"""
    tarea_id = arguments.get("id")
    
    if not tarea_id:
        raise ValidationError("El ID de la tarea es requerido")
    
    tareas = storage.cargar()
    
    # Buscar tarea
    tarea = None
    for t in tareas:
        if t.id == tarea_id:
            tarea = t
            break
    
    if not tarea:
        raise NotFoundError(f"No se encontró una tarea con ID: {tarea_id}")
    
    if tarea.completada:
        return [TextContent(
            type="text",
            text=f"ℹ️ La tarea '{tarea.titulo}' ya estaba completada."
        )]
    
    # Marcar como completada
    tarea.completada = True
    storage.guardar(tareas)
    
    logger.info(f"Tarea completada: {tarea.id} - {tarea.titulo}")
    
    return [TextContent(
        type="text",
        text=f"✅ Tarea completada!\n\n"
             f"**{tarea.titulo}**\n"
             f"ID: {tarea.id}"
    )]

async def main():
    """Punto de entrada con manejo de errores"""
    try:
        logger.info("=" * 50)
        logger.info("Iniciando servidor MCP de tareas...")
        logger.info("=" * 50)
        
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    
    except KeyboardInterrupt:
        logger.info("Servidor detenido por el usuario")
    except Exception as e:
        logger.critical(f"Error fatal al iniciar servidor: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
```

## Configuración Avanzada de Logging

### 1. Logging con Rotación de Archivos

```python
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

def configurar_logging():
    """Configura logging con rotación de archivos"""
    
    # Logger principal
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo (rotación por tamaño)
    file_handler = RotatingFileHandler(
        'logs/mcp_server.log',
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    
    # Handler para errores (rotación diaria)
    error_handler = TimedRotatingFileHandler(
        'logs/errors.log',
        when='midnight',
        interval=1,
        backupCount=30,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))
    
    # Agregar handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger
```

### 2. Logging Estructurado con JSON

```python
import json
import logging
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formatea logs como JSON"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Agregar datos personalizados
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        if hasattr(record, 'tool_name'):
            log_data['tool_name'] = record.tool_name
        
        return json.dumps(log_data, ensure_ascii=False)

# Uso
handler = logging.FileHandler('logs/structured.log')
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Logging con contexto
logger.info('Herramienta ejecutada', extra={
    'user_id': 'user123',
    'tool_name': 'crear_tarea'
})
```

### 3. Decorador para Logging Automático

```python
import functools
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

def log_execution(func: Callable) -> Callable:
    """Decorador para loggear ejecución de funciones"""
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"Iniciando {func_name}")
        logger.debug(f"Args: {args}, Kwargs: {kwargs}")
        
        try:
            result = await func(*args, **kwargs)
            logger.info(f"{func_name} completado exitosamente")
            return result
        
        except Exception as e:
            logger.error(
                f"Error en {func_name}: {e}",
                exc_info=True,
                extra={'args': args, 'kwargs': kwargs}
            )
            raise
    
    return wrapper

# Uso
@log_execution
async def crear_tarea(arguments: dict):
    # ... implementación
    pass
```

## Estrategias de Recuperación de Errores

### 1. Retry con Backoff Exponencial

```python
import asyncio
from typing import Callable, Any

async def retry_with_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0
) -> Any:
    """Reintenta una función con backoff exponencial"""
    
    for attempt in range(max_retries):
        try:
            return await func()
        
        except Exception as e:
            if attempt == max_retries - 1:
                logger.error(f"Fallo después de {max_retries} intentos: {e}")
                raise
            
            delay = min(base_delay * (2 ** attempt), max_delay)
            logger.warning(
                f"Intento {attempt + 1} falló: {e}. "
                f"Reintentando en {delay}s..."
            )
            await asyncio.sleep(delay)

# Uso
async def operacion_inestable():
    # ... código que puede fallar
    pass

resultado = await retry_with_backoff(operacion_inestable)
```

### 2. Circuit Breaker

```python
from datetime import datetime, timedelta
from enum import Enum

class CircuitState(Enum):
    CLOSED = "closed"      # Funcionando normalmente
    OPEN = "open"          # Circuito abierto, rechazando requests
    HALF_OPEN = "half_open"  # Probando si se recuperó

class CircuitBreaker:
    """Implementa el patrón Circuit Breaker"""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 60,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.success_threshold = success_threshold
        
        self.failures = 0
        self.successes = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func: Callable) -> Any:
        """Ejecuta función con protección de circuit breaker"""
        
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker en estado HALF_OPEN")
            else:
                raise Exception("Circuit breaker OPEN - servicio no disponible")
        
        try:
            result = await func()
            self._on_success()
            return result
        
        except Exception as e:
            self._on_failure()
            raise
    
    def _on_success(self):
        """Maneja llamada exitosa"""
        self.failures = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.successes += 1
            if self.successes >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.successes = 0
                logger.info("Circuit breaker cerrado - servicio recuperado")
    
    def _on_failure(self):
        """Maneja fallo"""
        self.failures += 1
        self.last_failure_time = datetime.now()
        self.successes = 0
        
        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker abierto después de {self.failures} fallos"
            )
    
    def _should_attempt_reset(self) -> bool:
        """Verifica si debe intentar resetear el circuito"""
        return (
            self.last_failure_time and
            datetime.now() - self.last_failure_time >= timedelta(seconds=self.timeout)
        )
```

## 📝 Ejercicios

### Ejercicio 1: Sistema de Errores Personalizado
Implementa un sistema de errores con:
- Jerarquía de excepciones personalizadas
- Códigos de error únicos
- Mensajes de error localizados

### Ejercicio 2: Dashboard de Logs
Crea un servidor MCP que:
- Analice archivos de log
- Genere estadísticas de errores
- Identifique patrones de fallos

### Ejercicio 3: Sistema de Monitoreo
Implementa:
- Métricas de rendimiento
- Alertas por email/slack
- Healthchecks automáticos

---

**Anterior:** [Lección 3.1 - Prompts](leccion1-prompts.md)  
**Siguiente:** [Lección 3.3 - Seguridad](leccion3-seguridad.md)

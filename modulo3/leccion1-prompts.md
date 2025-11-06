# Lección 3.1: Prompts Personalizados

## Introducción

Los **prompts** en MCP son plantillas predefinidas que facilitan la interacción con el modelo de IA. Permiten crear flujos de trabajo reutilizables y estandarizados, mejorando la experiencia del usuario.

## ¿Qué son los Prompts en MCP?

Los prompts son mensajes pre-configurados que:
- Guían al modelo en tareas específicas
- Proporcionan contexto consistente
- Simplifican tareas complejas
- Mejoran la calidad de las respuestas

## Estructura de un Prompt

```python
from mcp.types import Prompt, PromptMessage, TextContent

Prompt(
    name="nombre_del_prompt",
    description="Descripción clara del propósito",
    arguments=[
        {
            "name": "argumento1",
            "description": "Descripción del argumento",
            "required": True
        }
    ]
)
```

## Ejemplo Básico: Prompts de Código

```python
# src/prompts/code_prompts_server.py
"""
Servidor MCP con prompts para asistencia de código
"""

import asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Prompt,
    PromptMessage,
    TextContent,
    GetPromptResult
)
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

server = Server("code-prompts-mcp")

@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    """Lista todos los prompts disponibles"""
    return [
        Prompt(
            name="revisar_codigo",
            description="Revisa código en busca de errores, mejoras y buenas prácticas",
            arguments=[
                {
                    "name": "lenguaje",
                    "description": "Lenguaje de programación (python, javascript, java, etc.)",
                    "required": True
                },
                {
                    "name": "codigo",
                    "description": "Código a revisar",
                    "required": True
                }
            ]
        ),
        Prompt(
            name="explicar_codigo",
            description="Explica qué hace un fragmento de código de manera detallada",
            arguments=[
                {
                    "name": "codigo",
                    "description": "Código a explicar",
                    "required": True
                },
                {
                    "name": "nivel",
                    "description": "Nivel de detalle: basico, intermedio, avanzado",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="generar_tests",
            description="Genera casos de prueba para una función o clase",
            arguments=[
                {
                    "name": "codigo",
                    "description": "Código para el cual generar tests",
                    "required": True
                },
                {
                    "name": "framework",
                    "description": "Framework de testing (pytest, unittest, jest, etc.)",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="optimizar_codigo",
            description="Sugiere optimizaciones para mejorar el rendimiento",
            arguments=[
                {
                    "name": "codigo",
                    "description": "Código a optimizar",
                    "required": True
                },
                {
                    "name": "objetivo",
                    "description": "Objetivo: velocidad, memoria, legibilidad",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="documentar_funcion",
            description="Genera documentación completa para una función",
            arguments=[
                {
                    "name": "codigo",
                    "description": "Función a documentar",
                    "required": True
                },
                {
                    "name": "estilo",
                    "description": "Estilo de documentación: google, numpy, sphinx",
                    "required": False
                }
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    """Obtiene el prompt con los argumentos proporcionados"""
    
    if name == "revisar_codigo":
        lenguaje = arguments.get("lenguaje", "").lower()
        codigo = arguments.get("codigo", "")
        
        mensaje = f"""Por favor, revisa el siguiente código {lenguaje} y proporciona:

1. **Errores detectados**: Bugs, errores de sintaxis o lógica
2. **Mejoras sugeridas**: Optimizaciones y mejores prácticas
3. **Seguridad**: Posibles vulnerabilidades
4. **Legibilidad**: Sugerencias para código más limpio

Código a revisar:
```{lenguaje}
{codigo}
```

Proporciona una revisión detallada y constructiva."""

        return GetPromptResult(
            description=f"Revisión de código {lenguaje}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
    
    elif name == "explicar_codigo":
        codigo = arguments.get("codigo", "")
        nivel = arguments.get("nivel", "intermedio").lower()
        
        instrucciones = {
            "basico": "Explica de manera simple, como si fuera para un principiante",
            "intermedio": "Proporciona una explicación técnica pero accesible",
            "avanzado": "Incluye detalles técnicos, complejidad y consideraciones de diseño"
        }
        
        mensaje = f"""Explica qué hace el siguiente código.

Nivel de explicación: {nivel}
{instrucciones.get(nivel, instrucciones["intermedio"])}

Código:
```
{codigo}
```

Incluye:
- Propósito general
- Funcionamiento paso a paso
- Conceptos clave utilizados
- Casos de uso"""

        return GetPromptResult(
            description=f"Explicación de código (nivel {nivel})",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
    
    elif name == "generar_tests":
        codigo = arguments.get("codigo", "")
        framework = arguments.get("framework", "pytest")
        
        mensaje = f"""Genera casos de prueba completos para el siguiente código usando {framework}.

Código a testear:
```
{codigo}
```

Genera tests que cubran:
1. **Casos normales**: Funcionamiento esperado
2. **Casos límite**: Valores extremos
3. **Casos de error**: Manejo de excepciones
4. **Casos especiales**: Situaciones inusuales

Incluye comentarios explicando qué testea cada caso."""

        return GetPromptResult(
            description=f"Generación de tests con {framework}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
    
    elif name == "optimizar_codigo":
        codigo = arguments.get("codigo", "")
        objetivo = arguments.get("objetivo", "velocidad").lower()
        
        objetivos_desc = {
            "velocidad": "Optimiza para reducir el tiempo de ejecución",
            "memoria": "Optimiza para reducir el uso de memoria",
            "legibilidad": "Mejora la claridad y mantenibilidad del código"
        }
        
        mensaje = f"""Optimiza el siguiente código.

Objetivo principal: {objetivo}
{objetivos_desc.get(objetivo, objetivos_desc["velocidad"])}

Código original:
```
{codigo}
```

Proporciona:
1. Código optimizado
2. Explicación de las optimizaciones
3. Comparación de rendimiento esperado
4. Posibles trade-offs"""

        return GetPromptResult(
            description=f"Optimización de código ({objetivo})",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
    
    elif name == "documentar_funcion":
        codigo = arguments.get("codigo", "")
        estilo = arguments.get("estilo", "google").lower()
        
        mensaje = f"""Genera documentación completa para la siguiente función usando el estilo {estilo}.

Función:
```
{codigo}
```

La documentación debe incluir:
1. Descripción breve
2. Descripción detallada
3. Parámetros (tipos, descripciones)
4. Valores de retorno
5. Excepciones que puede lanzar
6. Ejemplos de uso
7. Notas adicionales si es necesario"""

        return GetPromptResult(
            description=f"Documentación (estilo {estilo})",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
    
    else:
        raise ValueError(f"Prompt no encontrado: {name}")

async def main():
    """Punto de entrada del servidor"""
    logger.info("Iniciando servidor de prompts de código...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Prompts con Contexto Dinámico

```python
@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "analisis_proyecto":
        # Cargar contexto del proyecto
        archivos = await listar_archivos_proyecto()
        estructura = await obtener_estructura()
        
        mensaje = f"""Analiza este proyecto:

**Estructura:**
{estructura}

**Archivos principales:**
{archivos}

Proporciona:
1. Resumen de la arquitectura
2. Tecnologías utilizadas
3. Puntos de mejora
4. Sugerencias de refactorización"""

        return GetPromptResult(
            description="Análisis completo del proyecto",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
```

## Prompts Conversacionales

```python
@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "asistente_debug":
        error = arguments.get("error", "")
        codigo = arguments.get("codigo", "")
        
        return GetPromptResult(
            description="Asistente de debugging interactivo",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Tengo el siguiente error:\n```\n{error}\n```"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        type="text",
                        text="Entiendo. ¿Podrías mostrarme el código que genera este error?"
                    )
                ),
                PromptMessage(
                    role="user",
                    content=TextContent(
                        type="text",
                        text=f"Aquí está el código:\n```\n{codigo}\n```"
                    )
                ),
                PromptMessage(
                    role="assistant",
                    content=TextContent(
                        type="text",
                        text="Voy a analizar el código y el error para ayudarte a solucionarlo."
                    )
                )
            ]
        )
```

## Mejores Prácticas

### 1. Nombres Descriptivos

```python
# ❌ Malo
Prompt(name="p1", description="hace algo")

# ✅ Bueno
Prompt(
    name="generar_api_rest",
    description="Genera una API REST completa con endpoints CRUD"
)
```

### 2. Argumentos Opcionales con Valores por Defecto

```python
arguments=[
    {
        "name": "formato",
        "description": "Formato de salida (json, yaml, xml). Default: json",
        "required": False
    }
]

# En el prompt
formato = arguments.get("formato", "json")
```

### 3. Validación de Argumentos

```python
@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "convertir":
        formato = arguments.get("formato", "").lower()
        
        formatos_validos = ["json", "yaml", "xml", "csv"]
        if formato not in formatos_validos:
            raise ValueError(
                f"Formato '{formato}' no válido. "
                f"Use uno de: {', '.join(formatos_validos)}"
            )
```

### 4. Mensajes Claros y Estructurados

```python
mensaje = f"""# Tarea: {tarea}

## Contexto
{contexto}

## Requisitos
1. {req1}
2. {req2}
3. {req3}

## Formato de Salida
{formato_esperado}

## Ejemplo
{ejemplo}"""
```

## Ejemplo Completo: Prompts de Escritura

```python
# src/prompts/writing_prompts.py
"""
Prompts para asistencia de escritura
"""

import asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Prompt, PromptMessage, TextContent, GetPromptResult

server = Server("writing-prompts-mcp")

@server.list_prompts()
async def list_prompts() -> List[Prompt]:
    return [
        Prompt(
            name="mejorar_texto",
            description="Mejora un texto corrigiendo gramática, estilo y claridad",
            arguments=[
                {
                    "name": "texto",
                    "description": "Texto a mejorar",
                    "required": True
                },
                {
                    "name": "tono",
                    "description": "Tono deseado: formal, casual, técnico, creativo",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="resumir",
            description="Resume un texto largo manteniendo los puntos clave",
            arguments=[
                {
                    "name": "texto",
                    "description": "Texto a resumir",
                    "required": True
                },
                {
                    "name": "longitud",
                    "description": "Longitud del resumen: corto, medio, largo",
                    "required": False
                }
            ]
        ),
        Prompt(
            name="traducir_tecnico",
            description="Traduce contenido técnico preservando terminología",
            arguments=[
                {
                    "name": "texto",
                    "description": "Texto a traducir",
                    "required": True
                },
                {
                    "name": "idioma_destino",
                    "description": "Idioma destino",
                    "required": True
                }
            ]
        )
    ]

@server.get_prompt()
async def get_prompt(name: str, arguments: dict) -> GetPromptResult:
    if name == "mejorar_texto":
        texto = arguments.get("texto", "")
        tono = arguments.get("tono", "profesional")
        
        mensaje = f"""Mejora el siguiente texto manteniendo un tono {tono}:

Texto original:
\"\"\"
{texto}
\"\"\"

Proporciona:
1. Texto mejorado
2. Lista de cambios realizados
3. Sugerencias adicionales"""

        return GetPromptResult(
            description=f"Mejora de texto (tono {tono})",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
    
    elif name == "resumir":
        texto = arguments.get("texto", "")
        longitud = arguments.get("longitud", "medio")
        
        limites = {
            "corto": "máximo 3 párrafos",
            "medio": "entre 4-6 párrafos",
            "largo": "entre 7-10 párrafos"
        }
        
        mensaje = f"""Resume el siguiente texto.

Longitud del resumen: {longitud} ({limites.get(longitud, limites['medio'])})

Texto completo:
\"\"\"
{texto}
\"\"\"

El resumen debe:
- Capturar los puntos principales
- Mantener la coherencia
- Ser claro y conciso
- Preservar información crítica"""

        return GetPromptResult(
            description=f"Resumen {longitud}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
    
    elif name == "traducir_tecnico":
        texto = arguments.get("texto", "")
        idioma = arguments.get("idioma_destino", "")
        
        mensaje = f"""Traduce el siguiente contenido técnico al {idioma}.

IMPORTANTE:
- Preserva términos técnicos en inglés cuando sea apropiado
- Mantén el formato del código
- Conserva nombres de variables y funciones
- Explica términos ambiguos

Texto a traducir:
\"\"\"
{texto}
\"\"\""""

        return GetPromptResult(
            description=f"Traducción técnica a {idioma}",
            messages=[
                PromptMessage(
                    role="user",
                    content=TextContent(type="text", text=mensaje)
                )
            ]
        )
    
    raise ValueError(f"Prompt no encontrado: {name}")

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## 📝 Ejercicios

### Ejercicio 1: Prompts de Desarrollo
Crea prompts para:
- Generar boilerplate de proyectos
- Crear modelos de datos
- Generar configuraciones
- Escribir scripts de deployment

### Ejercicio 2: Prompts de Análisis
Implementa prompts para:
- Análisis de complejidad de código
- Detección de code smells
- Sugerencias de refactorización
- Análisis de seguridad

### Ejercicio 3: Prompts Personalizados
Diseña prompts para tu flujo de trabajo:
- Plantillas de commits
- Generación de documentación
- Revisión de PRs
- Creación de issues

---

**Anterior:** [Módulo 2 - Resources](../modulo2/leccion3-resources.md)  
**Siguiente:** [Lección 3.2 - Manejo de Errores y Logging](leccion2-errores-logging.md)

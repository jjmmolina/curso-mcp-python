# Ejemplo: Calculadora MCP

```python
# src/ejemplos/calculadora_server.py
"""
Servidor MCP: Calculadora con operaciones básicas
"""

import asyncio
from typing import List
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, McpError
from pydantic import BaseModel, Field
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validación de argumentos
class OperacionBinariaArgs(BaseModel):
    a: float = Field(..., description="Primer número")
    b: float = Field(..., description="Segundo número")

class RaizArgs(BaseModel):
    numero: float = Field(..., ge=0, description="Número (debe ser positivo)")

class PotenciaArgs(BaseModel):
    base: float
    exponente: float

server = Server("calculadora-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
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
        ),
        Tool(
            name="restar",
            description="Resta dos números (a - b)",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="multiplicar",
            description="Multiplica dos números",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="dividir",
            description="Divide dos números (a / b). Retorna error si b es cero.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number", "description": "Divisor (no puede ser cero)"}
                },
                "required": ["a", "b"]
            }
        ),
        Tool(
            name="raiz_cuadrada",
            description="Calcula la raíz cuadrada de un número positivo",
            inputSchema={
                "type": "object",
                "properties": {
                    "numero": {
                        "type": "number",
                        "description": "Número positivo",
                        "minimum": 0
                    }
                },
                "required": ["numero"]
            }
        ),
        Tool(
            name="potencia",
            description="Calcula base elevada a exponente",
            inputSchema={
                "type": "object",
                "properties": {
                    "base": {"type": "number"},
                    "exponente": {"type": "number"}
                },
                "required": ["base", "exponente"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    try:
        if name == "sumar":
            args = OperacionBinariaArgs(**arguments)
            resultado = args.a + args.b
            return [TextContent(
                type="text",
                text=f"➕ {args.a} + {args.b} = {resultado}"
            )]
        
        elif name == "restar":
            args = OperacionBinariaArgs(**arguments)
            resultado = args.a - args.b
            return [TextContent(
                type="text",
                text=f"➖ {args.a} - {args.b} = {resultado}"
            )]
        
        elif name == "multiplicar":
            args = OperacionBinariaArgs(**arguments)
            resultado = args.a * args.b
            return [TextContent(
                type="text",
                text=f"✖️ {args.a} × {args.b} = {resultado}"
            )]
        
        elif name == "dividir":
            args = OperacionBinariaArgs(**arguments)
            
            if args.b == 0:
                return [TextContent(
                    type="text",
                    text="❌ Error: No se puede dividir por cero"
                )]
            
            resultado = args.a / args.b
            return [TextContent(
                type="text",
                text=f"➗ {args.a} ÷ {args.b} = {resultado}"
            )]
        
        elif name == "raiz_cuadrada":
            args = RaizArgs(**arguments)
            resultado = args.numero ** 0.5
            return [TextContent(
                type="text",
                text=f"√{args.numero} = {resultado}"
            )]
        
        elif name == "potencia":
            args = PotenciaArgs(**arguments)
            resultado = args.base ** args.exponente
            return [TextContent(
                type="text",
                text=f"{args.base}^{args.exponente} = {resultado}"
            )]
        
        else:
            raise McpError(code=-32601, message=f"Herramienta no encontrada: {name}")
    
    except McpError:
        raise
    except ValueError as e:
        raise McpError(code=-32602, message=f"Argumentos inválidos: {str(e)}")
    except Exception as e:
        logger.error(f"Error en {name}: {e}", exc_info=True)
        raise McpError(code=-32603, message="Error interno")

async def main():
    logger.info("Iniciando Calculadora MCP...")
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
```

## Pruebas

```python
# tests/test_calculadora.py
import pytest
from src.ejemplos.calculadora_server import (
    OperacionBinariaArgs,
    RaizArgs,
    PotenciaArgs
)

def test_suma():
    args = OperacionBinariaArgs(a=5, b=3)
    assert args.a + args.b == 8

def test_division_por_cero():
    args = OperacionBinariaArgs(a=10, b=0)
    # El servidor debe manejar esto

def test_raiz_negativa():
    with pytest.raises(ValueError):
        RaizArgs(numero=-4)

def test_potencia():
    args = PotenciaArgs(base=2, exponente=3)
    assert args.base ** args.exponente == 8
```

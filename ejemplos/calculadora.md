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
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["a", "b"]
            }
        )
    ]

if __name__ == "__main__":
    asyncio.run(main())
```
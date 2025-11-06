# Preguntas Frecuentes (FAQ)

## General

### ¿Qué es MCP exactamente?
MCP (Model Context Protocol) es un protocolo abierto que permite a los modelos de IA conectarse de manera estandarizada con herramientas y fuentes de datos externas. Piensa en ello como un "USB" para la IA - una forma universal de conectar diferentes componentes.

### ¿Por qué aprender MCP?
- Es el futuro de las integraciones de IA
- Creado por Anthropic (creadores de Claude)
- Protocolo abierto y en crecimiento
- Permite crear herramientas reutilizables
- Alta demanda en el mercado

### ¿Es difícil aprender MCP?
No, especialmente si ya sabes Python. Los conceptos básicos se pueden aprender en unos días, y con práctica, estarás creando servidores completos en semanas.

## Técnicas

### ¿Cuándo usar Tools vs Resources?
- **Tools**: Para acciones o cálculos (escribir, calcular, transformar)
- **Resources**: Para leer datos (configuración, documentación, logs)

### ¿Puedo usar MCP con otros modelos además de Claude?
Sí, MCP es un protocolo abierto. Cualquier cliente que implemente el protocolo puede usar servidores MCP. Actualmente, Claude Desktop es el cliente más maduro.

### ¿Necesito una base de datos?
No es obligatorio. Puedes usar archivos JSON, CSV, o incluso memoria (para servidores simples). Las bases de datos son recomendadas para aplicaciones en producción.

### ¿Cómo debugging un servidor MCP?
1. Usa logging extensivo
2. Prueba con stdio directamente
3. Revisa los logs de Claude Desktop
4. Usa herramientas como `mcp dev` (si está disponible)

### ¿Puedo combinar múltiples servidores MCP?
¡Sí! Los clientes pueden conectarse a múltiples servidores simultáneamente. Cada servidor se especializa en un dominio.

## Instalación y Configuración

### Error: "No module named 'mcp'"
```bash
# Asegúrate de que el entorno virtual está activado
# Windows
.\venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate

# Reinstala
pip install --upgrade mcp
```

### Mi servidor no aparece en Claude Desktop
1. Verifica la ruta en `claude_desktop_config.json`
2. Usa rutas absolutas (no relativas)
3. Reinicia Claude Desktop completamente
4. Revisa los logs en `%APPDATA%\Claude\logs` (Windows)

### ¿Cómo ver los logs de mi servidor?
Implementa logging en tu código:
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='mi_servidor.log',
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## Desarrollo

### ¿Cómo testear mi servidor sin Claude?
Puedes ejecutarlo directamente y simular entrada JSON-RPC, o usar pytest con mocks.

### ¿Puedo usar librerías externas?
¡Absolutamente! Usa httpx, aiofiles, sqlalchemy, etc. Solo inclúyelas en tu `requirements.txt`.

### ¿Cómo manejo secretos/API keys?
Usa variables de entorno:
```python
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('API_KEY')
```

### ¿Cuántos tools debería tener mi servidor?
No hay límite, pero mantén la cohesión. Un servidor debe enfocarse en un dominio (e.g., "servidor de archivos", "servidor de base de datos").

### ¿Puedo hacer llamadas HTTP desde un tool?
Sí, usa `httpx` para llamadas asíncronas:
```python
import httpx

async def consultar_api():
    async with httpx.AsyncClient() as client:
        response = await client.get('https://api.example.com')
        return response.json()
```

## Seguridad

### ¿Es seguro exponer archivos del sistema?
No expongas todo. Usa validación estricta y limita el acceso a directorios específicos:
```python
ALLOWED_DIR = Path("/ruta/permitida")

def validar_ruta(ruta):
    if not ruta.resolve().is_relative_to(ALLOWED_DIR):
        raise ValueError("Ruta no permitida")
```

### ¿Cómo evito inyección de código?
- Nunca uses `eval()` o `exec()` con entrada del usuario
- Valida todos los inputs con Pydantic
- Usa consultas parametrizadas para SQL

### ¿Los datos se envían a la nube?
Depende de tu implementación. Con servidores MCP locales y Claude Desktop, los datos se mantienen en tu máquina.

## Rendimiento

### ¿Mi servidor es lento?
- Usa operaciones asíncronas
- Implementa caching cuando sea apropiado
- Optimiza consultas a base de datos
- Usa logging para identificar cuellos de botella

### ¿Cuántos clientes pueden conectarse?
Un servidor MCP típicamente maneja un cliente a la vez (via stdio). Para múltiples clientes, considera HTTP/SSE.

## Producción

### ¿Puedo desplegar mi servidor en producción?
Sí, pero considera:
- Manejo robusto de errores
- Logging completo
- Monitoreo
- Backup de datos
- Tests automatizados

### ¿Cómo actualizo mi servidor sin interrumpir el servicio?
Para servidores stdio con Claude, necesitarás reiniciar Claude. Para servidores HTTP, puedes implementar rolling updates.

### ¿Necesito Docker?
No es obligatorio para desarrollo, pero es recomendado para producción y distribución.

## Comunidad y Recursos

### ¿Dónde puedo encontrar más ejemplos?
- [MCP Servers GitHub](https://github.com/modelcontextprotocol/servers)
- [MCP Documentation](https://modelcontextprotocol.io/)
- Este curso 😊

### ¿Puedo contribuir a MCP?
¡Sí! MCP es open source. Puedes:
- Crear servidores de ejemplo
- Contribuir al SDK
- Ayudar con documentación
- Compartir tus proyectos

### ¿Hay una comunidad de MCP?
Sí, busca:
- Discord de Anthropic
- GitHub Discussions
- Reddit (r/ClaudeAI)
- Twitter/X (#MCP)

## Solución de Problemas Comunes

### "JSON-RPC error"
Verifica que tu respuesta tenga el formato correcto. Usa siempre los tipos de MCP (`TextContent`, etc.).

### "Tool not found"
Asegúrate de que el nombre en `list_tools()` coincida exactamente con el usado en `call_tool()`.

### "Invalid arguments"
Valida el schema. Usa Pydantic para capturar errores temprano.

### El servidor se congela
Probablemente una operación bloqueante. Usa versiones async (`aiofiles`, `httpx.AsyncClient`, etc.).

## ¿Más Preguntas?

Si tienes una pregunta que no está aquí:
1. Revisa la documentación oficial de MCP
2. Busca en GitHub Issues
3. Pregunta en la comunidad
4. Abre un issue en el repositorio del curso

---

**¿No encontraste tu respuesta? ¡Pregunta en la comunidad!**

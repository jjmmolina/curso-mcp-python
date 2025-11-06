# Curso: Model Context Protocol (MCP) en Python

![CI](https://github.com/jjmmolina/curso-mcp-python/actions/workflows/ci.yml/badge.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB) ![MCP](https://img.shields.io/badge/MCP-1.2%2B-orange) ![Status](https://img.shields.io/badge/status-Activo-brightgreen)

## 📚 Descripción del Curso

Bienvenido al curso completo sobre **Model Context Protocol (MCP)** en Python. Este curso te enseñará desde los fundamentos hasta la implementación avanzada de servidores MCP, permitiéndote crear herramientas que extienden las capacidades de los asistentes de IA como Claude y GitHub Copilot.

**✨ Actualizado con las últimas prácticas oficiales de MCP**, incluyendo:
- 🚀 FastMCP para desarrollo simplificado
- 📋 Uso de `uv` como gestor de paquetes moderno
- ⚠️ Mejores prácticas de logging para servidores STDIO
- 🏗️ Terminología oficial (MCP Host, Client, Server)
- 🔄 Arquitectura interna y negociación de capacidades

## 🎯 Objetivos del Curso

- Comprender qué es MCP y por qué es importante
- Aprender a crear servidores MCP en Python
- Implementar herramientas (tools), recursos (resources) y prompts
- Integrar servidores MCP con clientes como Claude Desktop
- Desarrollar proyectos prácticos del mundo real

## 📋 Requisitos Previos

- Python 3.10 o superior
- Conocimientos básicos de Python
- Familiaridad con conceptos de programación asíncrona (async/await)
- Editor de código (VS Code recomendado)

## 🧭 Tabla de Contenidos

- [Descripción del Curso](#-descripción-del-curso)
- [Objetivos del Curso](#-objetivos-del-curso)
- [Requisitos Previos](#-requisitos-previos)
- [Estructura del Curso](#-estructura-del-curso)
- [Cómo Usar Este Curso](#-cómo-usar-este-curso)
- [Instalación](#-instalación)
- [Ejecutar los ejemplos](#-ejecutar-los-ejemplos)
- [Recursos Adicionales](#-recursos-adicionales)
- [Contribuciones](#-contribuciones)
- [Licencia](#-licencia)

## 📖 Estructura del Curso

### Módulo 1: Introducción a MCP
- [Lección 1.1: ¿Qué es MCP?](modulo1/leccion1-introduccion.md)
- [Lección 1.2: Arquitectura y Conceptos Clave](modulo1/leccion2-arquitectura.md)
- [Lección 1.3: Configuración del Entorno](modulo1/leccion3-configuracion.md)

### Módulo 2: Primeros Pasos
- [Lección 2.1: Tu Primer Servidor MCP](modulo2/leccion1-primer-servidor.md)
- [Lección 2.2: Implementando Tools](modulo2/leccion2-tools.md)
- [Lección 2.3: Trabajando con Resources](modulo2/leccion3-resources.md)

### Módulo 3: Características Avanzadas
- [Lección 3.1: Prompts Personalizados](modulo3/leccion1-prompts.md)
- [Lección 3.2: Manejo de Errores y Logging](modulo3/leccion2-errores-logging.md)
- [Lección 3.3: Seguridad y Mejores Prácticas](modulo3/leccion3-seguridad.md)

### Módulo 4: Proyectos Prácticos
- [Proyecto 1: Servidor de Gestión de Archivos](modulo4/proyecto1-archivos.md)
- [Proyecto 2: Integración con APIs Externas](modulo4/proyecto2-apis.md)
- [Proyecto 3: Sistema de Base de Datos](modulo4/proyecto3-database.md)
- [Proyecto Final: Proyecto Integrador](modulo4/proyecto-final.md)

## 🚀 Cómo Usar Este Curso

1. Lee cada lección en orden
2. Completa los ejercicios prácticos
3. Experimenta con el código de ejemplo
4. Construye los proyectos finales

## 📦 Instalación

### Opción 1: Con `uv` (Recomendado)

`uv` es un gestor de paquetes moderno y extremadamente rápido para Python:

```bash
# Instalar uv
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reiniciar el terminal después de la instalación

# Clonar el repositorio
git clone https://github.com/jjmmolina/curso-mcp-python.git
cd curso-mcp-python

# Crear entorno virtual
uv venv

# Activar entorno virtual (Windows)
.venv\Scripts\Activate.ps1

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
uv pip install -r requirements.txt
```

### Opción 2: Con pip tradicional

```bash
# Clonar el repositorio
git clone https://github.com/jjmmolina/curso-mcp-python.git
cd curso-mcp-python

# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual (Windows)
.venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Ejecutar los ejemplos

Consulta la guía de configuración y ejecución paso a paso (incluye instrucciones para Windows PowerShell):

- Ver: [SETUP.md](SETUP.md#-configurar-github-actions-opcional)

Ejemplos incluidos en este repositorio:
- Servidor de notas (Módulo 2): `src/tools/notas_server.py`
- Servidor de prompts de código (Módulo 3): `src/prompts/code_prompts_server.py`

Para ejecutarlos, abre una terminal en la raíz del proyecto y usa los comandos descritos en SETUP.md.

## 📚 Recursos Adicionales

- [Documentación oficial de MCP](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Ejemplos de la comunidad](https://github.com/modelcontextprotocol/servers)
- [Roadmap del curso](ROADMAP.md)
- [Guía de estudio](GUIA-ESTUDIO.md)

## 🤝 Contribuciones

Este es un curso de código abierto. Si encuentras errores o quieres mejorar el contenido, ¡las contribuciones son bienvenidas!

## 📝 Licencia

Este curso está bajo licencia MIT.

---

**¡Comencemos a aprender MCP en Python! 🐍✨**

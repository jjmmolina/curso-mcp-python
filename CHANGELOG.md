# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [1.0.0] - 2025-11-06

### ✨ Añadido
- Módulo 1: Introducción a MCP
  - Lección 1.1: ¿Qué es MCP?
  - Lección 1.2: Arquitectura y Conceptos Clave
  - Lección 1.3: Configuración del Entorno
- Módulo 2: Primeros Pasos
  - Lección 2.1: Tu Primer Servidor MCP
  - Lección 2.2: Implementando Tools
  - Lección 2.3: Trabajando con Resources
- Módulo 4: Proyecto Final
  - Sistema de Gestión de Proyectos
- Ejemplos:
  - Calculadora MCP
  - Sistema de Notas
  - Servidor de Documentación
  - Monitor de Logs
- Documentación:
  - README.md completo con badges
  - FAQ.md con preguntas frecuentes
  - GUIA-ESTUDIO.md con plan de 4 semanas
  - CONTRIBUTING.md con guía de contribución
  - LICENSE (MIT)
- Configuración:
  - requirements.txt con dependencias
  - .gitignore configurado
  - Templates de Issues y Pull Requests

### 📚 Recursos
- Enlaces a documentación oficial de MCP
- Enlaces a MCP Python SDK
- Guías de instalación para Windows, Linux y macOS
- Ejemplos de configuración de Claude Desktop

## [Unreleased]

### 🔜 Planeado
- Módulo 3: Características Avanzadas
  - Lección 3.1: Prompts Personalizados
  - Lección 3.2: Manejo de Errores y Logging
  - Lección 3.3: Seguridad y Mejores Prácticas
- Más ejemplos de código
- Videos tutoriales
- Ejercicios interactivos
- Tests automatizados

## [1.1.0] - 2025-11-06

### ✨ Añadido
- Módulo 3 completo: Características Avanzadas
  - Lección 3.1: Prompts Personalizados
  - Lección 3.2: Manejo de Errores y Logging
  - Lección 3.3: Seguridad y Mejores Prácticas
- Proyectos del Módulo 4 (plantillas iniciales)
  - Proyecto 1: Servidor de Gestión de Archivos
  - Proyecto 2: Integración con APIs Externas
  - Proyecto 3: Sistema de Base de Datos
- Ejemplos ejecutables en `src/`
  - `src/tools/notas_server.py`
  - `src/prompts/code_prompts_server.py`

### 🛠️ Cambiado
- README con tabla de contenidos, enlaces y sección para ejecutar ejemplos
- SETUP con guía de ejecución en Windows PowerShell
- requirements.txt con dependencias adicionales (cryptography, bleach)

### 🧹 Corregido
- Enlaces de navegación y consistencia en Módulo 4

### 🤖 Infraestructura
- CI inicial con GitHub Actions: lint (ruff) + tests (pytest)

## [Unreleased]

### 🔜 Planeado
- Más ejemplos de código (conversor, generador de contraseñas, TODO)
- Videos tutoriales y ejercicios interactivos
- Tests automatizados adicionales

## [1.2.0] - 2025-11-06

### ✨ Añadido
- **FastMCP**: Ejemplos y tutoriales usando FastMCP para desarrollo simplificado
- **Guía de `uv`**: Instrucciones para usar `uv` como gestor de paquetes moderno
- **Advertencias críticas sobre logging**: Documentación sobre el uso correcto de logging en servidores STDIO
- **Terminología oficial**: Actualización completa con términos oficiales (MCP Host, Client, Server)
- **Arquitectura interna**: Sección expandida sobre el flujo interno del servidor y negociación de capacidades
- **Estructura de proyecto**: Organización recomendada de archivos y carpetas

### 🛠️ Cambiado
- Módulo 1: Lección 1.1 actualizada con terminología oficial y ejemplos de FastMCP
- Módulo 1: Lección 1.2 mejorada con arquitectura interna y estructura de ficheros
- Módulo 1: Lección 1.3 actualizada con instalación usando `uv` y advertencias de logging
- Módulo 2: Lección 2.1 reescrita con ejemplos usando FastMCP y SDK base
- Módulo 2: Lección 2.2 mejorada con FastMCP, mejores prácticas y advertencias de logging
- requirements.txt actualizado a MCP SDK 1.2.0+ con soporte para FastMCP
- README actualizado con badges y menciones a las nuevas prácticas

### 📚 Recursos
- Enlaces a documentación oficial en https://modelcontextprotocol.io/
- Guías basadas en quickstart oficial de MCP
- Mejores prácticas alineadas con la especificación MCP

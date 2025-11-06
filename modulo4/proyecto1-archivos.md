# Proyecto 1: Servidor de Gestión de Archivos

## 🎯 Objetivo
Construir un servidor MCP que permita gestionar archivos locales de forma segura: listar, leer, crear, actualizar y eliminar (CRUD) dentro de un directorio permitido.

## 🧩 Requisitos
- MCP SDK para Python
- Manejo de rutas seguro (evitar path traversal)
- Validación con Pydantic
- Logging y manejo de errores

## 🏗️ Alcance
- Directorio raíz configurable (por ejemplo `data/`)
- Tools:
  - `listar_archivos(ruta?)`
  - `leer_archivo(ruta)`
  - `crear_archivo(ruta, contenido)`
  - `actualizar_archivo(ruta, contenido)`
  - `eliminar_archivo(ruta)`
- Recursos:
  - `resource:listado` con índice de archivos

## 🔐 Consideraciones de Seguridad
- Validar rutas con normalización (`os.path.normpath`)
- Restringir acceso al subárbol permitido
- Tamaño máximo de archivo
- Sanitización de salida

## 📝 Entregables
- Servidor MCP `src/files/file_server.py`
- Tests básicos con `pytest`
- Documentación corta en README del proyecto

## 🚀 Pasos Sugeridos
1. Definir modelos Pydantic para argumentos
2. Implementar validadores de ruta
3. Crear tools con manejo de errores específico
4. Agregar logging (INFO/ERROR)
5. Probar con archivos de ejemplo en `data/`

## ✅ Criterios de Aceptación
- No permite salir del directorio base
- Errores claros ante rutas inválidas
- Operaciones CRUD funcionan
- Logs útiles y no verbosos

## 🧪 Extensiones (Opcional)
- Búsqueda por patrón (glob)
- Previsualización paginada
- Versionado simple (copias con timestamp)

---

**Siguiente:** [Proyecto 2: Integración con APIs Externas](proyecto2-apis.md)

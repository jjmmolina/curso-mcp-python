# Proyecto 3: Sistema de Base de Datos

## 🎯 Objetivo
Desarrollar un servidor MCP con persistencia en base de datos (SQLite) para gestionar entidades (p. ej., tareas o notas) con operaciones CRUD y consultas avanzadas.

## 🧩 Requisitos
- ORM (`SQLAlchemy`) + `aiosqlite`
- Modelos de datos y validación con Pydantic
- Migraciones simples (opcional)
- Tests de integración básicos

## 🏗️ Alcance
- Entidad principal: `Tarea` o `Nota`
- Tools:
  - `crear_entidad(data)`
  - `listar_entidades(filtros?)`
  - `actualizar_entidad(id, data)`
  - `eliminar_entidad(id)`
- Resources:
  - `estadisticas` (conteos, por estado/prioridad)

## 🔐 Consideraciones de Seguridad
- Sanitizar entradas y salidas
- Límite de resultados y paginación
- Transacciones atómicas

## 📝 Entregables
- Servidor MCP `src/db/db_server.py`
- Esquema de BD y script de inicialización
- Pruebas con `pytest`

## 🚀 Pasos Sugeridos
1. Definir modelos ORM y esquemas Pydantic
2. Implementar capa de repositorio
3. Añadir tools con validación y errores claros
4. Agregar consultas filtradas y paginadas

## ✅ Criterios de Aceptación
- CRUD completo y funcional
- Consultas eficientes
- Tests básicos pasando

## 🧪 Extensiones (Opcional)
- Índices y optimizaciones
- Exportación a CSV/JSON
- Autenticación básica para tools

---

**Anterior:** [Proyecto 2: Integración con APIs](proyecto2-apis.md)  
**Siguiente:** [Proyecto Final](proyecto-final.md)

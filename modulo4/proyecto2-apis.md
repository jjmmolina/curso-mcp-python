# Proyecto 2: Integración con APIs Externas

## 🎯 Objetivo
Crear un servidor MCP que consuma API(s) externas (p. ej., clima, noticias o criptomonedas) y exponga tools para consultar y transformar los datos.

## 🧩 Requisitos
- Cliente HTTP asíncrono (`httpx`)
- Manejo de timeouts y reintentos
- Configuración con variables de entorno (`python-dotenv`)
- Caching simple opcional

## 🏗️ Alcance
- Tools:
  - `consultar_api(nombre, parametros)`
  - `normalizar_respuesta(datos)`
  - `guardar_cache(clave, datos?)`
  - `leer_cache(clave)`
- Prompts:
  - `resumen_datos(api, datos)`

## 🔐 Consideraciones de Seguridad
- No exponer API keys en logs ni errores
- Timeouts razonables (5-10s)
- Validar inputs antes de llamar a la API

## 📝 Entregables
- Servidor MCP `src/apis/api_server.py`
- Ejemplo de `.env.example`
- Documentación de endpoints soportados

## 🚀 Pasos Sugeridos
1. Definir adapter por API (ej. Open-Meteo)
2. Implementar cliente con `httpx.AsyncClient`
3. Agregar `retry` con backoff
4. Estandarizar salida y errores

## ✅ Criterios de Aceptación
- Manejo robusto de errores de red
- Normalización consistente de datos
- Configuración externalizada

## 🧪 Extensiones (Opcional)
- Circuit Breaker
- Métricas de rendimiento
- Cache TTL en disco

---

**Anterior:** [Proyecto 1: Gestión de Archivos](proyecto1-archivos.md)  
**Siguiente:** [Proyecto 3: Sistema de Base de Datos](proyecto3-database.md)

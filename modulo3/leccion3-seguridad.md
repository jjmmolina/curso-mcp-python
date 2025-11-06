# Lección 3.3: Seguridad y Mejores Prácticas

## Introducción

La seguridad es crítica en cualquier servidor MCP, especialmente cuando maneja datos sensibles o interactúa con sistemas externos. Esta lección cubre las mejores prácticas de seguridad.

## Principios de Seguridad

### 1. Principio de Mínimo Privilegio
Solo otorga los permisos necesarios para cada operación.

### 2. Defensa en Profundidad
Implementa múltiples capas de seguridad.

### 3. Validación de Entrada
Nunca confíes en los datos de entrada.

### 4. Fail Secure
En caso de error, falla de manera segura.

## Validación y Sanitización

### Validación Robusta con Pydantic

```python
# src/security/validation_server.py
"""
Servidor MCP con validación robusta
"""

from typing import Optional, List
from pydantic import (
    BaseModel,
    Field,
    validator,
    EmailStr,
    HttpUrl,
    constr,
    conint
)
from datetime import datetime
import re

class UsuarioSeguro(BaseModel):
    """Modelo de usuario con validaciones estrictas"""
    
    # Validación de email
    email: EmailStr
    
    # Nombre de usuario alfanumérico, 3-20 caracteres
    username: constr(
        regex=r'^[a-zA-Z0-9_]{3,20}$',
        min_length=3,
        max_length=20
    )
    
    # Contraseña fuerte (mínimo 8 caracteres, mayúscula, minúscula, número)
    password: constr(min_length=8)
    
    # Edad entre 13 y 120
    edad: conint(ge=13, le=120)
    
    # URL opcional
    website: Optional[HttpUrl] = None
    
    # Teléfono con formato específico
    telefono: Optional[str] = None
    
    @validator('password')
    def validar_password_fuerte(cls, v):
        """Valida que la contraseña sea fuerte"""
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe contener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe contener al menos una minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe contener al menos un número')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('La contraseña debe contener al menos un carácter especial')
        return v
    
    @validator('telefono')
    def validar_telefono(cls, v):
        """Valida formato de teléfono"""
        if v is None:
            return v
        
        # Remover espacios y guiones
        telefono_limpio = re.sub(r'[\s\-]', '', v)
        
        # Validar que solo contenga números y opcionalmente +
        if not re.match(r'^\+?[0-9]{10,15}$', telefono_limpio):
            raise ValueError(
                'Teléfono inválido. Debe contener 10-15 dígitos, opcionalmente con +'
            )
        
        return telefono_limpio

class ArchivoSeguro(BaseModel):
    """Validación de rutas de archivo"""
    
    ruta: str
    
    @validator('ruta')
    def validar_ruta_segura(cls, v):
        """Previene path traversal"""
        import os
        from pathlib import Path
        
        # Detectar intentos de path traversal
        if '..' in v or v.startswith('/'):
            raise ValueError('Ruta no permitida')
        
        # Normalizar ruta
        ruta_normalizada = os.path.normpath(v)
        
        # Verificar que no escape del directorio permitido
        directorio_base = Path('data')
        ruta_completa = (directorio_base / ruta_normalizada).resolve()
        
        if not str(ruta_completa).startswith(str(directorio_base.resolve())):
            raise ValueError('Acceso denegado a ruta fuera del directorio permitido')
        
        return str(ruta_normalizada)

class SQLQuerySegura(BaseModel):
    """Validación de queries SQL"""
    
    query: str
    parametros: Optional[dict] = {}
    
    @validator('query')
    def validar_query_segura(cls, v):
        """Previene SQL injection básico"""
        # Lista de palabras peligrosas
        palabras_prohibidas = [
            'DROP', 'DELETE', 'TRUNCATE', 'ALTER',
            'CREATE', 'INSERT', 'UPDATE', 'EXEC',
            'EXECUTE', 'GRANT', 'REVOKE'
        ]
        
        query_upper = v.upper()
        for palabra in palabras_prohibidas:
            if palabra in query_upper:
                raise ValueError(
                    f'Query contiene operación no permitida: {palabra}'
                )
        
        # Solo permitir SELECT
        if not query_upper.strip().startswith('SELECT'):
            raise ValueError('Solo se permiten queries SELECT')
        
        return v
```

## Sanitización de Salida

```python
import html
import bleach
from typing import Any

def sanitizar_html(texto: str) -> str:
    """Sanitiza HTML para prevenir XSS"""
    # Escapar HTML
    texto_escapado = html.escape(texto)
    return texto_escapado

def sanitizar_html_avanzado(texto: str) -> str:
    """Sanitiza HTML permitiendo tags seguros"""
    tags_permitidos = ['b', 'i', 'u', 'em', 'strong', 'p', 'br']
    atributos_permitidos = {}
    
    texto_limpio = bleach.clean(
        texto,
        tags=tags_permitidos,
        attributes=atributos_permitidos,
        strip=True
    )
    
    return texto_limpio

def sanitizar_salida(data: Any) -> Any:
    """Sanitiza cualquier tipo de dato para salida segura"""
    if isinstance(data, str):
        return sanitizar_html(data)
    elif isinstance(data, dict):
        return {k: sanitizar_salida(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitizar_salida(item) for item in data]
    else:
        return data
```

## Manejo Seguro de Credenciales

### NO almacenar credenciales en código

```python
# ❌ NUNCA HAGAS ESTO
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "password123"

# ✅ Usa variables de entorno
import os
from pathlib import Path

def cargar_configuracion():
    """Carga configuración de manera segura"""
    return {
        'api_key': os.getenv('API_KEY'),
        'db_password': os.getenv('DATABASE_PASSWORD'),
        'secret_key': os.getenv('SECRET_KEY')
    }

# Verificar que existen las variables necesarias
def verificar_configuracion():
    """Verifica que todas las variables requeridas existen"""
    variables_requeridas = ['API_KEY', 'DATABASE_PASSWORD', 'SECRET_KEY']
    
    faltantes = []
    for var in variables_requeridas:
        if not os.getenv(var):
            faltantes.append(var)
    
    if faltantes:
        raise ValueError(
            f"Variables de entorno faltantes: {', '.join(faltantes)}"
        )
```

### Uso de archivos .env

```python
# Instalar: pip install python-dotenv
from dotenv import load_dotenv
import os

# Cargar variables desde .env
load_dotenv()

API_KEY = os.getenv('API_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')

# .env (NO subir a git)
"""
API_KEY=sk-1234567890abcdef
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=mi-secreto-super-seguro
"""

# .env.example (SÍ subir a git)
"""
API_KEY=tu_api_key_aqui
DATABASE_URL=postgresql://user:pass@localhost/db
SECRET_KEY=genera_un_secreto_aleatorio
"""
```

## Cifrado de Datos Sensibles

```python
from cryptography.fernet import Fernet
import base64
import os

class EncriptadorSeguro:
    """Maneja cifrado de datos sensibles"""
    
    def __init__(self, key: bytes = None):
        if key is None:
            key = os.getenv('ENCRYPTION_KEY')
            if key:
                key = key.encode()
            else:
                # Generar nueva clave (guardar de manera segura!)
                key = Fernet.generate_key()
                print(f"IMPORTANTE: Guarda esta clave: {key.decode()}")
        
        self.cipher = Fernet(key)
    
    def encriptar(self, datos: str) -> str:
        """Encripta datos"""
        datos_bytes = datos.encode()
        encriptado = self.cipher.encrypt(datos_bytes)
        return base64.b64encode(encriptado).decode()
    
    def desencriptar(self, datos_encriptados: str) -> str:
        """Desencripta datos"""
        datos_bytes = base64.b64decode(datos_encriptados.encode())
        desencriptado = self.cipher.decrypt(datos_bytes)
        return desencriptado.decode()

# Uso
encriptador = EncriptadorSeguro()

# Encriptar dato sensible
password = "mi_password_secreto"
password_encriptado = encriptador.encriptar(password)

# Guardar password_encriptado en BD
# ...

# Recuperar y desencriptar cuando se necesite
password_original = encriptador.desencriptar(password_encriptado)
```

## Control de Acceso y Autenticación

```python
# src/security/auth_server.py
"""
Servidor MCP con autenticación básica
"""

import asyncio
import hashlib
import secrets
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent, McpError

class SessionManager:
    """Gestiona sesiones de usuario"""
    
    def __init__(self, timeout_minutes: int = 30):
        self.sessions: Dict[str, dict] = {}
        self.timeout = timedelta(minutes=timeout_minutes)
    
    def crear_sesion(self, user_id: str) -> str:
        """Crea una nueva sesión"""
        token = secrets.token_urlsafe(32)
        self.sessions[token] = {
            'user_id': user_id,
            'created_at': datetime.now(),
            'last_activity': datetime.now()
        }
        return token
    
    def validar_sesion(self, token: str) -> Optional[str]:
        """Valida una sesión y retorna user_id si es válida"""
        if token not in self.sessions:
            return None
        
        sesion = self.sessions[token]
        
        # Verificar timeout
        if datetime.now() - sesion['last_activity'] > self.timeout:
            del self.sessions[token]
            return None
        
        # Actualizar última actividad
        sesion['last_activity'] = datetime.now()
        return sesion['user_id']
    
    def cerrar_sesion(self, token: str):
        """Cierra una sesión"""
        if token in self.sessions:
            del self.sessions[token]

class PasswordHasher:
    """Maneja hashing seguro de contraseñas"""
    
    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> tuple:
        """Hashea una contraseña"""
        if salt is None:
            salt = secrets.token_bytes(32)
        
        # Usar PBKDF2 con muchas iteraciones
        hash_obj = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations=100000
        )
        
        return hash_obj, salt
    
    @staticmethod
    def verificar_password(password: str, hash_guardado: bytes, salt: bytes) -> bool:
        """Verifica una contraseña"""
        hash_nuevo, _ = PasswordHasher.hash_password(password, salt)
        return secrets.compare_digest(hash_nuevo, hash_guardado)

# Servidor con autenticación
server = Server("auth-mcp")
session_manager = SessionManager()

# Simulación de base de datos de usuarios
usuarios_db = {
    'admin': {
        'hash': b'...',  # Hash de la contraseña
        'salt': b'...',  # Salt usado
        'role': 'admin'
    }
}

def verificar_autenticacion(arguments: dict) -> str:
    """Verifica que el usuario esté autenticado"""
    token = arguments.get('_auth_token')
    
    if not token:
        raise McpError(
            code=-32000,
            message="Token de autenticación requerido"
        )
    
    user_id = session_manager.validar_sesion(token)
    
    if not user_id:
        raise McpError(
            code=-32000,
            message="Sesión inválida o expirada"
        )
    
    return user_id

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Ejecuta herramientas con verificación de autenticación"""
    
    # Herramientas públicas (no requieren auth)
    if name == "login":
        return await login(arguments)
    
    # Verificar autenticación para otras herramientas
    user_id = verificar_autenticacion(arguments)
    
    if name == "logout":
        return await logout(arguments)
    elif name == "datos_protegidos":
        return await obtener_datos_protegidos(user_id)
    else:
        raise McpError(code=-32601, message=f"Herramienta no encontrada: {name}")

async def login(arguments: dict) -> List[TextContent]:
    """Login de usuario"""
    username = arguments.get('username')
    password = arguments.get('password')
    
    if not username or not password:
        raise McpError(
            code=-32602,
            message="Username y password son requeridos"
        )
    
    # Verificar usuario
    if username not in usuarios_db:
        raise McpError(code=-32000, message="Credenciales inválidas")
    
    usuario = usuarios_db[username]
    
    # Verificar password
    if not PasswordHasher.verificar_password(
        password,
        usuario['hash'],
        usuario['salt']
    ):
        raise McpError(code=-32000, message="Credenciales inválidas")
    
    # Crear sesión
    token = session_manager.crear_sesion(username)
    
    return [TextContent(
        type="text",
        text=f"✅ Login exitoso. Token: {token}"
    )]

async def logout(arguments: dict) -> List[TextContent]:
    """Logout de usuario"""
    token = arguments.get('_auth_token')
    session_manager.cerrar_sesion(token)
    
    return [TextContent(
        type="text",
        text="✅ Sesión cerrada exitosamente"
    )]

async def obtener_datos_protegidos(user_id: str) -> List[TextContent]:
    """Retorna datos protegidos para usuario autenticado"""
    return [TextContent(
        type="text",
        text=f"🔒 Datos protegidos para usuario: {user_id}"
    )]
```

## Rate Limiting

```python
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict

class RateLimiter:
    """Implementa rate limiting"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window = timedelta(seconds=window_seconds)
        self.requests: Dict[str, list] = defaultdict(list)
    
    def permitir_request(self, client_id: str) -> bool:
        """Verifica si se permite el request"""
        ahora = datetime.now()
        
        # Limpiar requests antiguos
        self.requests[client_id] = [
            timestamp for timestamp in self.requests[client_id]
            if ahora - timestamp < self.window
        ]
        
        # Verificar límite
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Registrar request
        self.requests[client_id].append(ahora)
        return True
    
    def requests_restantes(self, client_id: str) -> int:
        """Retorna requests restantes"""
        ahora = datetime.now()
        
        # Limpiar requests antiguos
        self.requests[client_id] = [
            timestamp for timestamp in self.requests[client_id]
            if ahora - timestamp < self.window
        ]
        
        return max(0, self.max_requests - len(self.requests[client_id]))

# Uso
rate_limiter = RateLimiter(max_requests=100, window_seconds=60)

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    client_id = arguments.get('client_id', 'default')
    
    if not rate_limiter.permitir_request(client_id):
        raise McpError(
            code=-32000,
            message="Rate limit excedido. Intenta más tarde."
        )
    
    # Procesar request...
```

## Mejores Prácticas Generales

### 1. Principio de Menor Exposición

```python
# ❌ Exponer información sensible en errores
try:
    conectar_bd(username="admin", password="secret123")
except Exception as e:
    return f"Error: {e}"  # Podría exponer credenciales

# ✅ Mensajes de error genéricos
try:
    conectar_bd(username, password)
except Exception as e:
    logger.error(f"Error de conexión: {e}", exc_info=True)
    return "Error de conexión a la base de datos"
```

### 2. Timeout en Operaciones

```python
import asyncio

async def operacion_con_timeout(timeout_segundos: int = 30):
    """Operación con timeout"""
    try:
        async with asyncio.timeout(timeout_segundos):
            resultado = await operacion_larga()
            return resultado
    except asyncio.TimeoutError:
        logger.warning("Operación excedió el timeout")
        raise McpError(
            code=-32000,
            message="Operación demoró demasiado"
        )
```

### 3. Auditoría de Acciones

```python
class AuditLogger:
    """Registra acciones para auditoría"""
    
    @staticmethod
    def log_action(user_id: str, action: str, details: dict):
        """Registra una acción"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip': details.get('ip_address')
        }
        
        # Guardar en log de auditoría
        with open('logs/audit.log', 'a') as f:
            import json
            f.write(json.dumps(log_entry) + '\n')

# Uso
@server.call_tool()
async def call_tool(name: str, arguments: dict):
    user_id = verificar_autenticacion(arguments)
    
    # Auditar acción
    AuditLogger.log_action(
        user_id=user_id,
        action=name,
        details={'arguments': arguments}
    )
    
    # Procesar...
```

## 📝 Ejercicios

### Ejercicio 1: Sistema de Permisos
Implementa:
- Roles de usuario (admin, user, guest)
- Permisos por herramienta
- Verificación de permisos antes de ejecutar

### Ejercicio 2: Validador de Entrada
Crea validadores para:
- Direcciones de email
- URLs
- Números de tarjeta de crédito
- Códigos postales

### Ejercicio 3: Sistema de Auditoría Completo
Desarrolla:
- Log de todas las acciones
- Dashboard de auditoría
- Alertas de acciones sospechosas
- Reportes de seguridad

---

**Anterior:** [Lección 3.2 - Errores y Logging](leccion2-errores-logging.md)  
**Siguiente:** [Módulo 4 - Proyectos](../modulo4/proyecto-final.md)

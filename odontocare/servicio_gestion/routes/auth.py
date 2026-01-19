'''
Endpoint para /auth de la API 'OdontoCare' que realiza:
    - validación de credenciales
    - generación y validación de tokens (JWT)
    - manejo de errores de acceso
    - decorador de autorización de acceso por rol
'''

from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, jsonify, request
from jwt import encode, decode
from jwt import exceptions
from werkzeug.security import check_password_hash


from servicio_gestion.models.usuarios import Usuario
import servicio_gestion.config as config

# Crea una instancia de Blueprint para 'auth_bp'
auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

# Roles permitidos
allowed_roles =['admin']

# ---------- Genera token -----------------

def generate_jwt_token(username, rol):
    'genera un token JWT para un usuario'

    # Construye el payload con el ROL incluido
    payload = {
        'sub': username,
        'rol': rol,
        'iat': datetime.now(timezone.utc),
        'exp': datetime.now(timezone.utc) + config.Config.JWT_EXPIRATION_DELTA
    }

    token = encode(payload, key=config.Config.JWT_SECRET_KEY, algorithm='HS256')

    return token

# ---- Login: recupera usuario y password ----

# Define la ruta para /auth/login
@auth_bp.route('/login', methods=['POST'])
def login():
    'endpoint auth/login'
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    rol = data.get('rol')

    # Buscar al usuario en la base de datos
    user = Usuario.query.filter_by(username=username).first()

    # Validar credenciales

    if not user:
        return jsonify({'error': f'Usuario: {username} no encontrado.'}), 404

    if not check_password_hash(user.password, password):
        return jsonify({'error': 'Password incorrecta'}), 401

    # Credenciales correctas
    token = generate_jwt_token(username, rol)
    expiration = datetime.now(timezone.utc) + config.Config.JWT_EXPIRATION_DELTA

    return jsonify({'token':token,
                    'rol':rol,
                    'expires_at':expiration.isoformat(timespec='hours') + 'Z'}), 200


# ----- Decorador de autorización por rol -----

def requiere_rol(allowed_roles):
    'rol requerido para acceder al endpoint'
    def decorador_interno(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Extrae el token del header Authorization: Bearer <token>
            auth_header = request.headers.get('Authorization', '')
            partes = auth_header.split()
            if len(partes) != 2 or partes[0].lower() != 'bearer':
                return jsonify({'mensaje': 'Token no proporcionado'}), 401
            token = partes[1]

            # Decodificar y validar el token
            try:
                payload = decode(token, key=config.Config.JWT_SECRET_KEY, algorithms=['HS256'])
                rol_del_usuario = payload.get('rol')
                if rol_del_usuario not in allowed_roles:
                    return jsonify({'mensaje': 'Permiso denegado'}), 403
            except exceptions.ExpiredSignatureError:
                return jsonify({'mensaje': 'El token ha expirado'}), 401
            except exceptions.InvalidTokenError:
                return jsonify({'mensaje': 'Token inválido'}), 401

            # Si todo OK
            return f(*args, **kwargs)
        return wrapper
    return decorador_interno

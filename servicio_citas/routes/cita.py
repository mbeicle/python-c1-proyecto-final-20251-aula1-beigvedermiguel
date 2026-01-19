'''
Endpoints para /cita de la API 'OdontoCare' que realiza:
    - creación, actualización, consulta y eliminación de citas
    - validación de disponibilidad de doctores y centros médicos
    - reglas operativas para evitar conflictos en la agenda
    - respuestas en formato JSON
'''

from datetime import datetime
from functools import wraps
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from jwt import decode, exceptions

import requests

from servicio_gestion.extensions import db
from servicio_citas.models.citas import CitaMedica
from servicio_citas.config import Config
from servicio_citas.schemas import cita_schema


# Crea una instancia de Blueprint para 'citas_bp'
citas_bp = Blueprint('citas_bp', __name__, url_prefix='/citas')

# Roles permitidos
allowed_roles_crear = ['admin', 'secretaria']
allowed_roles_listar = ['admin', 'secretaria', 'medico']
allowed_roles_cancelar = ['admin', 'secretaria']

# URL base para comunicarse con otros servicios
BASE_URL = "http://localhost:5001"

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
                payload = decode(token, key=Config.JWT_SECRET_KEY, algorithms=['HS256'])
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


# --------- Ruta para crear cita -------------

# Define la ruta para POST /agendar
@citas_bp.route('/agendar', methods=['POST'])
@requiere_rol(allowed_roles_crear)
def add_cita():
    'endpoint POST para agendar una cita'

    # Obtiene los datos JSON del cuerpo de la petición
    data = request.get_json()

    # Asegura que la petición contiene datos JSON
    if not request.is_json:
        return jsonify({'message': 'Missing JSON in request'}), 400

    # Extrae y valida los datos del cuerpo de la petición (request body)
    try:
        # Parsea la fecha
        data['fecha'] = datetime.strptime(data['fecha'], "%d-%m-%Y %H:%M")
        # Validar y cargar los datos
        validated_data = cita_schema.cita_medica_schema.load(data)
        # Los datos validados están en validated_data (como diccionario de Python)
    except ValidationError as err:
        # Manejar errores de validación
        return jsonify(err.messages), 400

    # Si la validación es exitosa, se utilizan los datos (validated_data)
    # para crear una nueva cita.

    # Extrae el token del header Authorization: Bearer <token>
    auth_header = request.headers.get('Authorization', '')
    partes = auth_header.split()
    token = partes[1]
    # Si el token es válido
    if token:
        # Crea las cabeceras con el Bearer Token
        headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
                }

    # Se busca al paciente mediante una petición GET
    url = f'{BASE_URL}/admin/paciente/{validated_data['id_paciente']}'
    response = requests.get(url, headers=headers, timeout=5)

    # Se verifica si la petición fue exitosa
    if response.status_code == 200:
        # Decodificar la respuesta JSON en un diccionario o lista de Python
        paciente = response.json()
    else:
        # Maneja códigos de error
        return jsonify({'error': f'Error al obtener datos del paciente: {response.status_code}',
                        'message': 'El paciente no existe en la base de datos'})

    # Se comprueba si está activo
    if paciente['Paciente']['estado'] == 'inactivo':
        return jsonify({'error': 'Usuario no está activo'}), 200

    # Se busca al doctor mediante una petición GET
    url = f'{BASE_URL}/admin/doctor/{validated_data['id_doctor']}'
    response = requests.get(url, headers=headers, timeout=3)
    # Verifica si la petición fue exitosa
    if response.status_code == 200:
        # Decodificar la respuesta JSON en un diccionario o lista de Python
        doctor = response.json()
    else:
        # Maneja códigos de error
        return jsonify({'error': f'Error al obtener datos del doctor: {response.status_code}',
                        'message': 'El doctor no existe en la base de datos'})

    # Se busca el centro médico mediante una petición GET
    url = f'{BASE_URL}/admin/centro_medico/{validated_data['id_centro']}'
    response = requests.get(url, headers=headers, timeout=3)
    # Verifica si la petición fue exitosa
    if response.status_code == 200:
        # Decodificar la respuesta JSON en un diccionario o lista de Python
        centro_medico = response.json()
    else:
        # Maneja códigos de error
        return jsonify({'error': f'Error al obtener datos del centro médico: {response.status_code}',
                        'message': 'El Centro Médico no existe en la base de datos'})
    
    # Busca citas del doctor en esa misma fecha para ver si está libre
    cita = CitaMedica.query.filter_by(fecha=validated_data['fecha'],
                                      id_doctor=validated_data['id_doctor']).first()
    if cita:
        return jsonify({'error': 'El Doctor ya tiene una cita a esa hora en esa fecha'}), 200

    new_cita = CitaMedica(
                          fecha = validated_data['fecha'],
                          motivo = validated_data['motivo'],
                          estado = validated_data['estado'],
                          id_usuario = validated_data['id_usuario'],
                          id_paciente = validated_data['id_paciente'],
                          id_doctor = validated_data['id_doctor'],
                          id_centro = validated_data['id_centro']
                        )

    try:
        db.session.add(new_cita)
        db.session.commit()
        return jsonify({"message": "Cita registrada",
                        'cita': new_cita.to_dict()}), 201
    except Exception as e:
        return jsonify({'message': f'Error {e} al guardar la cita en la base de datos'}), 500


# --------- Rutas para consultar citas -------------

# Define la ruta para GET /listar citas con query params
@citas_bp.route('/listar_citas', methods=['GET'])
@requiere_rol(allowed_roles_listar)
def get_citas():
    'endpoint GET para listar citas'

    citas_salida = ''
    # Obtiene los valores de los parámetros de consulta
    id_doctor = request.args.get('id_doctor')
    fecha = request.args.get('fecha')
    id_centro = request.args.get('id_centro')
    estado = request.args.get('estado')
    id_paciente = request.args.get('id_paciente')

    # Decodifica el token para saber quién hace la petición
    # Extrae el token del header Authorization: Bearer <token>
    auth_header = request.headers.get('Authorization', '')
    partes = auth_header.split()
    token = partes[1]
    payload = decode(token, key=Config.JWT_SECRET_KEY, algorithms=['HS256'])
    username = payload.get('sub')
    user_rol = payload.get('rol')

    # Si el token es válido
    if token:
        # Crea las cabeceras con el Bearer Token
        headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
                }

    # Aplica los filtros a las citas según el rol del peticionario y
    # el 'query param' presente en la petición
    if id_doctor:
        if user_rol == 'admin':
            try:
                # Filtra las citas por doctor si se proporciona id_doctor en el query
                citas_filtradas = CitaMedica.query.filter_by(id_doctor=id_doctor,
                                                             estado='activa').all()
                if not citas_filtradas:
                    return jsonify({'error': 'El doctor no tiene citas agendadas'}), 201
                citas_salida = [cita.to_dict() for cita in citas_filtradas]
            except ValueError:
                return jsonify({'error': 'Parámetro id_doctor inválido'}), 400
        elif user_rol == 'medico':
            # Se recupera el username del peticionario
            url = f'{BASE_URL}/admin/doctor/username?username={username}'
            # Se busca al doctor mediante una petición GET
            response = requests.get(url, headers=headers, timeout=3)
            # Verifica si la petición fue exitosa
            if response.status_code == 200:
                # Decodificar la respuesta JSON en un diccionario o lista de Python
                doctor = response.json()
            else:
                # Maneja códigos de error
                return jsonify({'error': f'Error al obtener datos: {response.status_code}'})
            # Se comprueba que existe
            if not doctor:
                return jsonify({'error': 'El Doctor no existe en la Base de Datos'}), 200
            # Se obtiene el id_doctor_peticionario de la respuesta
            id_doctor_peticionario = doctor['id_doctor']
            # Si el solicitante coincide con el id_doctor para el que se piden las citas
            if id_doctor == str(id_doctor_peticionario):
                try:
                    # Se filtran las citas por doctor proporcionando id_doctor en el query
                    citas_filtradas = CitaMedica.query.filter_by(id_doctor=id_doctor,
                                                                estado='activa').all()
                    if not citas_filtradas:
                        return jsonify({'error': 'El doctor no tiene citas agendadas'}), 201
                except ValueError:
                    return jsonify({'error': 'Parámetro id_doctor inválido'}), 400
                # Se obtienen las citas buscadas
                citas_salida = [cita.to_dict() for cita in citas_filtradas]
            else:
                return jsonify({'error': 'No está autorizado a ver las citas de otro doctor.'}), 400
        else:
            return jsonify({'error': 'No está autorizado a listar las citas por doctor.'}), 400

    if fecha:
        if user_rol == 'admin' or user_rol == 'secretaria':
            # Filtra las citas por fecha si se proporciona fecha en el query
            try:
                # Convierte la cadena de fecha a un objeto datetime.datetime
                fecha_obj = datetime.strptime(fecha, '%d-%m-%Y %H:%M:%S')
                # Filtra las citas por doctor si se proporciona id_doctor en el query
                citas_filtradas = CitaMedica.query.filter_by(fecha=fecha_obj).all()
                if not citas_filtradas:
                    return jsonify({'error': 'No hay citas agendadas en esa fecha'}), 201
                citas_salida = [cita.to_dict() for cita in citas_filtradas]
            except ValueError:
                return jsonify({'error': 'Formato de fecha inválido. Use: DD-MM-YYYY HH:MM:SS'}), 400
        else:
            return jsonify({'error': 'No está autorizado a listar las citas por fecha.'}), 400

    if id_paciente:
        if user_rol == 'admin':
            # Filtra las citas por paciente si se proporciona id_paciente en el query
            try:
                citas_filtradas = CitaMedica.query.filter_by(id_paciente=id_paciente).all()
                if not citas_filtradas:
                    return jsonify({'error': 'No hay citas agendadas para ese paciente'}), 201
                citas_salida = [cita.to_dict() for cita in citas_filtradas]
            except ValueError:
                return jsonify({'error': 'Parámetro id_paciente inválido'}), 400
        else:
            return jsonify({'error': 'No está autorizado a listar las citas de un paciente.'}), 400

    if id_centro:
        if user_rol == 'admin':
            # Filtra las citas por centro mèdico si se proporciona id_centro en el query
            try:
                citas_filtradas = CitaMedica.query.filter_by(id_centro=id_centro).all()
                citas_salida = [cita.to_dict() for cita in citas_filtradas]
            except ValueError:
                return jsonify({'error': 'Parámetro id_centro inválido'}), 400
        else:
            return jsonify({'error': 'No está autorizado a listar los centros médicos.'}), 400

    if estado:
        if user_rol == 'admin':
        # Filtra las citas por estado si se proporciona en el query
            try:
                citas_filtradas = CitaMedica.query.filter_by(estado=estado).all()
                citas_salida = [cita.to_dict() for cita in citas_filtradas]
            except ValueError:
                return jsonify({'error': 'Parámetro estado inválido'}), 400
        else:
            return jsonify({'error': 'No está autorizado a listar las citas por estado.'}), 400

    if citas_salida == [] or citas_salida == '':
        return jsonify({'error': 'La consulta no contiene ningún resultado.'}), 200
    # Devuelve el resultado de la consulta
    # no debe devolver todas las citas
    return jsonify({'Citas':citas_salida}), 200



# --------- Ruta para modificar datos en una cita -------------

@citas_bp.route('/modificar/<int:id_cita>', methods=['PUT'])
@requiere_rol(allowed_roles_crear)
def update_cita(id_cita):
    """
    endpoint PUT para actualizar la información de una cita existente
    """

    # Obtiene la cita por su ID
    cita = CitaMedica.query.get_or_404(id_cita)

    # Extrae los datos a actualizar del body de la solicitud
    data = request.get_json()

    # Actualiza los atributos del registro con los datos recibidos
    if 'fecha' in data:
        # Convierte la cadena de fecha a un objeto datetime.datetime
        fecha_obj = datetime.strptime(data['fecha'], '%d-%m-%Y %H:%M:%S')
        # Busca citas del doctor en esa misma fecha para ver si está libre
        if 'id_doctor' in data:
            cita_verif = CitaMedica.query.filter_by(id_doctor=data['id_doctor'],
                                                    fecha=fecha_obj).first()
            if cita_verif:
                return jsonify({'error': 'El Doctor ya tiene una cita a esa hora en esa fecha'}), 200
        else:
            cita_verif = CitaMedica.query.filter_by(id_doctor=cita.id_doctor,
                                                    fecha=fecha_obj).first()
            if cita_verif:
                return jsonify({'error': 'El Doctor ya tiene una cita a esa hora en esa fecha'}), 200
        # Se modifica la fecha de la cita
        cita.fecha = fecha_obj
    # Si se quiere cambiar el paciente de la cita
    if 'id_paciente' in data:
        # Extrae el token del header Authorization: Bearer <token>
        auth_header = request.headers.get('Authorization', '')
        partes = auth_header.split()
        token = partes[1]
        # Si el token es válido
        if token:
            # Crea las cabeceras con el Bearer Token
            headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                    }
        # Se busca al paciente mediante una petición GET
        url = f'{BASE_URL}/admin/paciente/{data['id_paciente']}'
        response = requests.get(url, headers=headers, timeout=3)
        # Se verifica si la petición fue exitosa
        if response.status_code == 200:
            # Decodificar la respuesta JSON en un diccionario o lista de Python
            paciente = response.json()
        else:
            # Maneja códigos de error
            return jsonify({'error': f'Error al obtener datos: {response.status_code}'})
        # Se comprueba que existe el paciente
        if not paciente:
            return jsonify({'error': 'El paciente no existe en la Base de Datos'}), 200
        #return jsonify({'paciente': paciente})
        # Se comprueba si está activo
        if paciente['Paciente']['estado'] == 'inactivo':
            return jsonify({'error': 'Paciente no está activo',
                            'message': 'Utilice otra id_paciente para actualizar la cita.'}), 200
        # En caso contrario, se modifica el paciente de la cita
        cita.id_paciente = data['id_paciente']
    # Si se quiere cambiar al doctor de la cita
    if 'id_doctor' in data:
        cita_verif = CitaMedica.query.filter_by(id_doctor=data['id_doctor'],
                                                fecha=cita.fecha).first()
        if cita_verif:
            return jsonify({'error': 'El Doctor ya tiene una cita a esa hora en esa fecha'}), 200
        else:
            # Se modifica el doctor de la cita
            cita.id_doctor = data['id_doctor']

    # Si se quiere cambiar el centro médico de la cita
    if 'id_centro' in data:
        # Se modifica el centro médico de la cita
        cita.id_centro = data['id_centro']
    print(cita.to_dict())
    try:
        db.session.commit()
        return jsonify({'message': 'Cita actualizada',
                        'cita': cita.to_dict()}), 201
    except Exception as e:
        return jsonify({'message': f'Error {e} al guardar la cita en la base de datos'}), 500


# --------- Ruta para cancelar una cita -------------

# Define la ruta para PUT /cancelar
@citas_bp.route('/cancelar/<int:id_cita>', methods=['PUT'])
@requiere_rol(allowed_roles_cancelar)
def cancelar_cita(id_cita):
    'endpoint PUT para cancelar una cita'

    # Obtiene la cita por su ID
    cita = CitaMedica.query.get(id_cita)

     # Si la cita existe
    if cita:
        # Comprobar si está activa
        if cita.estado == 'cancelada':
            return jsonify({'error': 'La cita ya estaba cancelada.'}), 200
        # Se modifica el estado de la cita y se actualiza
        cita.estado = 'cancelada'
        try:
            db.session.commit()
            return jsonify({'message': 'Cita cancelada',
                            'cita': cita.to_dict()}), 201
        except Exception as e:
            return jsonify({'error': f'Error {e} al guardar la cita en la base de datos'}), 500
    return jsonify({'error': 'La cita que quieres cancelar, no existe.'}), 404

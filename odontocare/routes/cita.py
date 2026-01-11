'''
Endpoints para /cita de la API 'OdontoCare' que realiza:
    - creación, actualización, consulta y eliminación de citas
    - validación de disponibilidad de doctores y centros médicos
    - reglas operativas para evitar conflictos en la agenda
    - respuestas en formato JSON
'''

from datetime import datetime
from jwt import decode
from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from odontocare.models.usuarios import Usuario
from odontocare.models.doctores import Doctor
from odontocare.models.pacientes import Paciente
from odontocare.models.centros_medicos import CentroMedico
from odontocare.models.citas import CitaMedica

from odontocare.config import Config, EstadoUsuario
from odontocare.schemas import cita_schema
from odontocare.extensions import db
from odontocare.routes.auth import requiere_rol


# Crea una instancia de Blueprint para 'citas_bp'
citas_bp = Blueprint('citas_bp', __name__, url_prefix='/citas')

# Roles permitidos
allowed_roles_crear = ['admin', 'paciente']
allowed_roles_listar = ['admin', 'secretaria', 'medico']
allowed_roles_cancelar = ['admin', 'secretaria']

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

    # Se busca al paciente en la base de datos
    paciente = Paciente.query.filter_by(id_usuario=validated_data['id_usuario']).first()
    # Se comprueba que existe
    if not paciente:
        return jsonify({'error': 'El paciente no existe en la Base de Datos'}), 200
    # Se comprueba si está activo
    if paciente.estado == EstadoUsuario.INACTIVO:
        return jsonify({'error': 'Usuario no está activo'}), 200
    # Se busca al doctor en la base de datos
    doctor = Doctor.query.filter_by(id_doctor=validated_data['id_doctor']).first()
    if not doctor:
        return jsonify({'error': 'El Doctor no existe en la Base de Datos'}), 200
    # Se busca el centro médico en la base de datos
    centro_medico = CentroMedico.query.filter_by(id_centro=validated_data['id_centro']).first()
    if not centro_medico:
        return jsonify({'error': 'El Centro Médico no existe en la Base de Datos'}), 200

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


# --------- Rutas para consultar una cita -------------

# Define la ruta para GET /consultar una cita
@citas_bp.route('/consultar/<int:id_cita>', methods=['GET'])
@requiere_rol('paciente')
def get_cita(id_cita):
    """
    Endpoint GET para obtener los datos de un registro individual de cita.
    """

    # Obtiene los datos JSON del cuerpo de la petición
    cita = CitaMedica.query.get(id_cita)

    # Si se encuentra la cita, se devuelven los datos
    if cita:
        data_cita = cita.to_dict()
        return jsonify({'Cita': data_cita})
    # Si no se encuentra, error 404
    return jsonify({'error': 'Cita no encontrada'}), 404


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
            # Se recupera el id_doctor del peticionario
            usuario = Usuario.query.filter_by(username=username).first()
            id = usuario.id_usuario
            if usuario:
                # Accede al objeto Doctor a través del atributo 'id_usuario'
                doctor = Doctor.query.filter_by(id_usuario=id).first()
                id_doct = str(doctor.id_doctor)
            # Si el solicitante coincide con el id_doctor para el que se piden las citas
            if id_doctor == id_doct:
                try:
                    # Filtra las citas por doctor si se proporciona id_doctor en el query
                    citas_filtradas = CitaMedica.query.filter_by(id_doctor=id_doctor,
                                                                 estado='activa').all()
                    if not citas_filtradas:
                        return jsonify({'error': 'El doctor no tiene citas agendadas'}), 201
                    citas_salida = [cita.to_dict() for cita in citas_filtradas]
                except ValueError:
                    return jsonify({'error': 'Parámetro id_doctor inválido'}), 400
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
    if 'id_paciente' in data:
        # Buscar al paciente en la base de datos
        paciente = Paciente.query.filter_by(id_paciente=data['id_paciente']).first()
        # Comprobar si está activo
        if paciente.estado == EstadoUsuario.INACTIVO:
            return jsonify({'error': 'Paciente no está activo',
                            'message': 'Utilice otra id_paciente para actualizar la cita.'}), 200
        # Se modifica el paciente de la cita
        cita.id_paciente = data['id_paciente']
    if 'id_doctor' in data:
        cita_verif = CitaMedica.query.filter_by(id_doctor=data['id_doctor'],fecha=cita.fecha).first()
        if cita_verif:
            return jsonify({'error': 'El Doctor ya tiene una cita a esa hora en esa fecha'}), 200
        else:
            # Se modifica el doctor de la cita
            cita.id_doctor = data['id_doctor']
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

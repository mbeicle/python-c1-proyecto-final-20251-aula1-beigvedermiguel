'''
Endpoints para /admin de la API 'OdontoCare' que realiza:
    - creación de centros_médicos, pacientes y doctores
    - carga de datos
    - consulta para todo tipo de registros:
        - búsqueda individual por ID
        - visualización de lista completa de registros
'''

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from werkzeug.security import generate_password_hash

from servicio_gestion.extensions import db
from servicio_gestion.models.usuarios import Usuario
from servicio_gestion.models.doctores import Doctor
from servicio_gestion.models.pacientes import Paciente
from servicio_gestion.models.centros_medicos import CentroMedico
from servicio_gestion.routes.auth import requiere_rol
from servicio_gestion.schemas import doctor_schema, paciente_schema
from servicio_gestion.schemas import centro_medico_schema, user_schema

# Crea una instancia de Blueprint
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')

# Roles permitidos
allowed_roles =['admin', 'secretaria']
allowed_roles_doctor_username =['admin', 'medico']


# --------- Rutas para /admin/usuario -------------

@admin_bp.route('/usuario', methods=['POST'])
@requiere_rol(allowed_roles)
def add_usuario():
    """
    Endpoint POST para añadir un registro individual de usuario.
    """

    # Obtiene los datos JSON del cuerpo de la petición
    data = request.get_json()

    # Asegura que la petición contiene datos JSON
    if not request.is_json:
        return jsonify({'message': 'Missing JSON in request'}), 400

    # Asegura que la contraseña no está vacía
    if data['password']:
        # Hashear la contraseña antes de validar
        password = generate_password_hash(data['password'], method='scrypt:32768:8:1')
        data['password'] = password
    else:
        return jsonify({'error': 'El campo "password" no debe estar vacío.'}), 400

    # Extrae y valida los datos del cuerpo de la petición (request body)
    try:
        # Validar y cargar los datos
        validated_data = user_schema.usuario_schema.load(data)
        # Los datos validados están en validated_data (como diccionario de Python)
    except ValidationError as err:
        # Manejar errores de validación
        return jsonify(err.messages), 400

    # Si la validación es exitosa, se utilizan los datos (validated_data)
    # para crear un nuevo usuario.

    # Verifica si el usuario ya existe en la base de datos
    if Usuario.query.filter_by(username=validated_data['username']).first():
        return jsonify({'error': 'El usuario ya existe'}), 409

    new_user = Usuario(
                       username=validated_data['username'],
                       password=validated_data['password'],
                       rol=validated_data['rol']
                       )

    try:
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuario registrado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': f'Error {e} al guardar el usuario en la base de datos'}), 500


@admin_bp.route('/usuario/<int:id_usuario>', methods=['GET'])
@requiere_rol(allowed_roles)
def get_usuario(id_usuario):
    """
    Endpoint GET para obtener los datos de un registro individual de usuario
    proporcionando el 'id_usuario'.
    """

    # Obtiene los datos JSON del cuerpo de la petición
    usuario = Usuario.query.get(id_usuario)

    # Si se encuentra al usuario, se devuelven sus datos
    if usuario:
        usuario_data = usuario.to_dict()
        return jsonify({'Usuario': usuario_data})
    # Si no se encuentra, error 404
    return jsonify({'error': 'Usuario no encontrado '}), 404


@admin_bp.route('/usuarios', methods=['GET'])
@requiere_rol(allowed_roles)
def get_usuarios():
    """
    Endpoint GET para obtener los datos de todos los usuarios.
    """

    # Obtiene parámetros de paginación de la URL.
    # Los valores por defecto: página 1 y 5 elementos por página
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Usa el método paginate() en la consulta
    pagination = Usuario.query.paginate(page=page, per_page=per_page, error_out=False)

    # Serializa los elementos de la página actual
    usuarios_on_page = [usuario.to_dict() for usuario in pagination.items]

    if page > pagination.pages:
        return jsonify({
            'error': 'La página solicitada no contiene usuarios.'
        })
    return jsonify({
                    'usuarios': usuarios_on_page,
                    'pagination': {
                                'current_page': pagination.page,
                                'total_pages': pagination.pages,
                                'total_usuarios': pagination.total,
                                'per_page': pagination.per_page
                                }
        })


# --------- Rutas para /admin/doctor -------------

@admin_bp.route('/doctor', methods=['POST'])
@requiere_rol(allowed_roles)
def add_doctor():
    """
    Endpoint POST para añadir un registro individual de doctor.
    Antes de añadir el doctor, lo añade como usuario con los datos del doctor.
    """

    # Obtiene los datos JSON del cuerpo de la petición
    # La petición debe incluir los datos de doctor y de usuario
    data = request.get_json()

    # Asegura que la petición contiene datos JSON
    if not request.is_json:
        return jsonify({'message': 'Missing JSON in request'}), 400

    # Extrae y valida los datos del cuerpo de la petición (request body)
    # Primero extrae los datos de Usuario
    username = data.get('username')
    password = data.get('password')
    rol = data.get('rol')
    # Después extrae los datos de Doctor
    nombre = data.get('nombre')
    especialidad = data.get('especialidad')

    # Asegura que la contraseña no está vacía
    if password:
        # Hashea la contraseña antes de validar
        password = generate_password_hash(data['password'], method='scrypt:32768:8:1')
    else:
        return jsonify({'error': 'El campo "password" no debe estar vacío.'}), 400

    # Comienza la creación de los registros
    try:
        # Valida los datos de Usuario
        try:
            user_data = ({'username': username,'password': password, 'rol': rol})
            validated_data_user = user_schema.usuario_schema.load(user_data)
            # Los datos validados están en validated_data_user (como diccionario de Python)
        except ValidationError as err:
            # Manejar errores de validación
            return jsonify(err.messages), 400

        # Si la validación es exitosa, se utilizan los datos (validated_data_user)
        # para crear un nuevo usuario.

        # Verifica si el usuario ya existe en la base de datos
        if Usuario.query.filter_by(username=validated_data_user['username']).first():
            return jsonify({'error': 'El usuario ya existe'}), 409

        # Crea el nuevo usuario
        new_user = Usuario(
                            username=validated_data_user['username'],
                            password=validated_data_user['password'],
                            rol = validated_data_user['rol']
                        )

        # Se guarda en la base de datos
        db.session.add(new_user)

        # Averiguamos el último id_usuario existente en la tabla 'usuarios'
        last_user = Usuario.query.order_by(Usuario.id_usuario.desc()).first()

        if last_user:
            id_usuario = last_user.id_usuario + 1
        else:
            print("La tabla de usuarios está vacía.")

        # Valida los datos de Doctor
        try:
            doctor_data = ({'nombre': nombre,'especialidad': especialidad, 'id_usuario': id_usuario})
            validated_data_doctor = doctor_schema.doc_schema.load(doctor_data)
            # Los datos validados están en validated_data_doctor (como diccionario de Python)
        except ValidationError as err:
            # Manejar errores de validación
            return jsonify(err.messages), 400

        # Si la validación es exitosa, se utilizan los datos (validated_data)
        # para crear un nuevo doctor.

        # Verifica si el doctor ya existe en la base de datos
        if Doctor.query.filter_by(nombre=validated_data_doctor['nombre']).first():
            return jsonify({'error': 'El doctor ya existe'}), 409

        # Crea el nuevo doctor
        new_doctor = Doctor(
                            id_usuario=validated_data_doctor['id_usuario'],
                            nombre=validated_data_doctor['nombre'],
                            especialidad=validated_data_doctor['especialidad']
                        )

        # Se guarda en la base de datos
        db.session.add(new_doctor)

        # Se hace commit de los dos registros en la base de datos
        db.session.commit()

        return jsonify({'message': 'Usuario y Doctor registrados exitosamente',
                        'id_usuario': id_usuario,
                        'id_doctor': new_doctor.id_doctor
                    }), 201

    except Exception as e:
         # En caso de error, se hace rollback para no dejar registros de doctor inconsistentes
        db.session.rollback()
        # Después, se elimina el usuario que ya se había creado
        user_to_delete = Usuario.query.get(id_usuario)
        print(id_usuario)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit() # Confirmar la eliminación del usuario
        # Se informa del error
        return jsonify({'message': f'Error {e} al guardar usuario/doctor en la base de datos'}), 500


@admin_bp.route('/doctor/<int:id_doctor>', methods=['GET'])
@requiere_rol(allowed_roles)
def get_doctor(id_doctor):
    """
    Endpoint GET para obtener los datos de un registro individual de doctor.
    """

    # Obtiene el id_doctor del parámetro de ruta
    doctor = Doctor.query.get(id_doctor)
    # Si se encuentra al usuario, se devuelven sus datos
    if doctor:
        doctor_data = doctor.to_dict()
        return jsonify({'Doctor': doctor_data})
    # Si no se encuentra, error 404
    return jsonify({'error': 'Doctor no encontrado '}), 404


# Define la ruta GET para buscar un doctor por su 'username' con query params
@admin_bp.route('/doctor/username', methods=['GET'])
@requiere_rol(allowed_roles_doctor_username)
def get_doctor_username():
    """
    Endpoint GET para obtener los datos de un registro individual de doctor 
    buscando por 'username' mediante query params.
    """

    # Obtiene los valores de los parámetros de consulta
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Se requiere el parámetro username'}), 400

    # Consulta la base de datos para encontrar al usuario por username
    usuario = Usuario.query.filter_by(username=username).first()
    if usuario:
        usuario_data = usuario.to_dict()
        id_usuario = usuario_data['id_usuario']
    # Si no se encuentra, error 404
    else:
        return jsonify({'error': 'Usuario no encontrado.'}), 404

    # Consulta la base de datos para encontrar al doctor por id_usuario
    doctor = Doctor.query.filter_by(id_usuario=id_usuario).first()
    if doctor:
        doctor_data = doctor.to_dict()
        #id_doctor = doctor_data.id_doctor
        return jsonify(doctor_data)
    # Si no se encuentra, error 404
    return jsonify({'error': 'Doctor no encontrado '}), 404


@admin_bp.route('/doctores', methods=['GET'])
@requiere_rol(allowed_roles)
def get_doctores():
    """
    Endpoint GET para obtener los datos de todos los doctores.
    """

    # Obtiene parámetros de paginación de la URL.
    # Los valores por defecto: página 1 y 5 elementos por página
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Usa el método paginate() en la consulta
    pagination = Doctor.query.paginate(page=page, per_page=per_page, error_out=False)

    # Serializa los elementos de la página actual
    doctores_on_page = [doctor.to_dict() for doctor in pagination.items]

    if page > pagination.pages:
        return jsonify({
            'error': 'La pagina solicitada no contiene doctores.'
        })

    return jsonify({
                    'doctores': doctores_on_page,
                    'pagination': {
                                'current_page': pagination.page,
                                'total_pages': pagination.pages,
                                'total_doctores': pagination.total,
                                'per_page': pagination.per_page
                                }
        })


# --------- Rutas para /admin/paciente -------------

@admin_bp.route('/paciente', methods=['POST'])
@requiere_rol(allowed_roles)
def add_paciente():
    """
    Endpoint POST para añadir un registro individual de paciente.
    Antes de añadir el paciente, lo añade como usuario con los datos del paciente.
    """

    # Obtiene los datos JSON del cuerpo de la petición
    # La petición debe incluir los datos de paciente y de usuario
    data = request.get_json()

    # Asegura que la petición contiene datos JSON
    if not request.is_json:
        return jsonify({'message': 'Missing JSON in request'}), 400

    # Extrae y valida los datos del cuerpo de la petición (request body)
    # Primero extrae los datos de Usuario
    username = data.get('username')
    password = data.get('password')
    rol = data.get('rol')
    # Después extrae los datos de Paciente
    nombre = data.get('nombre')
    telefono = data.get('telefono')
    estado = data.get('estado')

    # Asegura que la contraseña no está vacía
    if password:
        # Hashea la contraseña antes de validar
        password = generate_password_hash(data['password'], method='scrypt:32768:8:1')
    else:
        return jsonify({'error': 'El campo "password" no debe estar vacío.'}), 400

    # Comienza la creación de los registros
    try:
        # Valida los datos de Usuario
        try:
            user_data = ({'username': username,'password': password, 'rol': rol})
            validated_data_user = user_schema.usuario_schema.load(user_data)
            # Los datos validados están en validated_data (como diccionario de Python)
        except ValidationError as err:
            # Manejar errores de validación
            return jsonify(err.messages), 400

        # Verifica si el usuario ya existe en la base de datos
        if Usuario.query.filter_by(username=validated_data_user['username']).first():
            return jsonify({'error': 'El usuario ya existe'}), 409

        # Si los datos son correctos, se utilizan para crear el usuario

        # Crea el nuevo usuario
        new_user = Usuario(
                            username=validated_data_user['username'],
                            password=validated_data_user['password'],
                            rol = validated_data_user['rol']
                        )
        # Se guarda en la base de datos
        db.session.add(new_user)
        db.session.commit()

        # Ahora ya está disponible el 'id_usuario' para dar de alta al Paciente
        id_usuario = new_user.id_usuario

        # Valida los datos de Paciente
        try:
            paciente_data = ({
                              'nombre': nombre,
                              'telefono': telefono, 
                              'estado': estado, 
                              'id_usuario': id_usuario
                             })
            validated_data_paciente = paciente_schema.pacient_schema.load(paciente_data)
            # Los datos validados están en validated_data_paciente (como diccionario de Python)
        except ValidationError as err:
            # Manejar errores de validación
            return jsonify(err.messages), 400

        # Verifica si el paciente ya existe en la base de datos
        if Paciente.query.filter_by(nombre=validated_data_paciente['nombre']).first():
            return jsonify({'error': 'El paciente ya existe'}), 409

        # Si los datos son correctos, se utilizan para crear el paciente

        # Crea el nuevo paciente
        new_paciente = Paciente(
                            id_usuario=validated_data_paciente['id_usuario'],
                            nombre=validated_data_paciente['nombre'],
                            telefono=validated_data_paciente['telefono'],
                            estado=validated_data_paciente['estado']
                        )
        # Se guarda en la base de datos
        db.session.add(new_paciente)
        db.session.commit()

        return jsonify({'message': 'Usuario y Paciente registrados exitosamente',
                        'id_usuario': id_usuario,
                        'id_paciente': new_paciente.id_paciente
                        }), 201

    except Exception as e:
        # En caso de error, hacer rollback para no dejar rastro del registro del paciente
        db.session.rollback()
        # Después debemos deshacer el guardado del registro de usuario
        usuario_a_eliminar = Usuario.query.filter_by(id=id_usuario).one()
        db.session.delete(usuario_a_eliminar)
        db.session.commit()
        return jsonify({'message': f'Error {e} al guardar usuario/paciente en la base de datos'}), 500


@admin_bp.route('/paciente/<int:id_paciente>', methods=['GET'])
@requiere_rol(allowed_roles)
def get_paciente(id_paciente):
    """
    Endpoint GET para obtener los datos de un registro individual de paciente.
    """

    # Realiza la petición con el id_paciente
    paciente = Paciente.query.get(id_paciente)
    # Si se encuentra al paciente, se devuelven sus datos
    if paciente:
        paciente.estado = paciente.estado.value
        paciente_data = paciente.to_dict()
        return jsonify({'Paciente': paciente_data})
    # Si no se encuentra, error 404
    return jsonify({'error': 'Paciente no encontrado '}), 404


@admin_bp.route('/pacientes', methods=['GET'])
@requiere_rol(allowed_roles)
def get_pacientes():
    """
    Endpoint GET para obtener los datos de todos los pacientes.
    """

    # Obtiene parámetros de paginación de la URL.
    # Los valores por defecto: página 1 y 5 elementos por página
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Usa el método paginate() en la consulta
    pagination = Paciente.query.paginate(page=page, per_page=per_page, error_out=False)

    # Serializa los elementos de la página actual
    pacientes_on_page = []
    for paciente in pagination.items:
        paciente.estado = paciente.estado.value
        pacientes_on_page.append(paciente.to_dict())

    if page > pagination.pages:
        return jsonify({
            'error': 'La pagina solicitada no contiene pacientes.'
        })

    return jsonify({
                    'pacientes': pacientes_on_page,
                    'pagination': {
                                'current_page': pagination.page,
                                'total_pages': pagination.pages,
                                'total_pacientes': pagination.total,
                                'per_page': pagination.per_page
                                }
        })


# --------- Rutas para /admin/centro_medico -------------

@admin_bp.route('/centro_medico', methods=['POST'])
@requiere_rol(allowed_roles)
def add_centro():
    """
    Endpoint POST para añadir un registro individual de centro_medico.
    """

    # Obtiene los datos JSON del cuerpo de la petición
    data = request.get_json()

    # Asegura que la petición contiene datos JSON
    if not request.is_json:
        return jsonify({'message': 'Missing JSON in request'}), 400

    # Extrae y valida los datos del cuerpo de la petición (request body)
    try:
        # Validar y cargar los datos
        validated_data = centro_medico_schema.centr_medico_schema.load(data)
        # Los datos validados están en validated_data (como diccionario de Python)
    except ValidationError as err:
        # Manejar errores de validación
        return jsonify(err.messages), 400

    # Si la validación es exitosa, se utilizan los datos (validated_data)
    # para crear un nuevo centro médico.

    # Verifica si el centro médico ya existe en la base de datos
    if CentroMedico.query.filter_by(nombre=validated_data['nombre']).first():
        return jsonify({'error': 'El centro médico ya existe'}), 409

    new_centro_medico = CentroMedico(
                                    nombre=validated_data['nombre'],
                                    direccion=validated_data['direccion']
                                    )

    try:
        db.session.add(new_centro_medico)
        db.session.commit()
        return jsonify({'message': 'Centro Médico registrado exitosamente'}), 201
    except Exception as e:
        return jsonify({'error': f'Error {e} al guardar Cenro Medico en la base de datos'}), 500


@admin_bp.route('/centro_medico/<int:id_centro>', methods=['GET'])
@requiere_rol(allowed_roles)
def get_centro(id_centro):
    """
    Endpoint GET para obtener los datos de un registro individual de centro médico.
    """

    # Obtiene los datos JSON del cuerpo de la petición
    centro = CentroMedico.query.get(id_centro)
    # Si se encuentra al usuario, se devuelven sus datos
    if centro:
        centro_data = centro.to_dict()
        return jsonify({'Centro Médico': centro_data})
    # Si no se encuentra, error 404
    return jsonify({'error': 'Centro Médico no encontrado'}), 404


@admin_bp.route('/centros_medicos', methods=['GET'])
@requiere_rol(allowed_roles)
def get_centros():
    """
    Endpoint GET para obtener los datos de todos los centros médicos.
    """

    # Obtiene parámetros de paginación de la URL.
    # Los valores por defecto: página 1 y 5 elementos por página
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 5, type=int)

    # Usa el método paginate() en la consulta
    pagination = CentroMedico.query.paginate(page=page, per_page=per_page, error_out=False)

    # Serializa los elementos de la página actual
    centros_on_page = [centro.to_dict() for centro in pagination.items]

    if page > pagination.pages:
        return jsonify({
            'error': 'La página solicitada no contiene Centros Médicos.'
        })

    return jsonify({
                    'centros médicos': centros_on_page,
                    'pagination': {
                                'current_page': pagination.page,
                                'total_pages': pagination.pages,
                                'total_centros': pagination.total,
                                'per_page': pagination.per_page
                                }
        })

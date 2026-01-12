'''
Pruebas unitarias para verificar funciones realizadas por el endpoint /admin 
para pacientes.
'''

import json

def test_admin_add_paciente(client, auth_login_admin):
    'Prueba con éxito el endpoint /admin/paciente'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }

    # Se crean los datos del nuevo paciente
    new_paciente = {
                'username': 'user_paciente_1',
                'password': 'pass_user_paciente_1',
                'rol': 'paciente',
                'nombre': 'Jesús Gómez Narro',
                'telefono': '+34 670 89 54 32',
                'estado': 'activo'
               }

    # Se realiza la petición POST
    response = client.post('/admin/paciente', headers=headers, data=json.dumps(new_paciente))

    # Se verifica el resultado
    assert response.status_code == 201
    assert 'Usuario y Paciente registrados exitosamente' in response.json.get('message', '')


def test_admin_add_paciente_data_missing(client, auth_login_admin):
    'Prueba el endpoint /admin/paciente con datos faltantes'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo paciente
    new_paciente = {
                'username': 'user_paciente_2',
                'password': 'pass_user_paciente_2',
                'rol': 'paciente',
                'telefono': '+34 670 89 54 32',
                'estado': 'activo'
               }

    # Se realiza la petición POST
    response = client.post('/admin/paciente', headers=headers, data=json.dumps(new_paciente))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Field may not be null.' in response.json.get('nombre', '')


def test_admin_add_paciente_validate_error(client, auth_login_admin):
    'Prueba el endpoint /admin/paciente con un error de validación'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo paciente
    new_paciente = {
                'username': 'user_paciente_3',
                'password': 'pass_user_paciente_3',
                'rol': 'paciente',
                'nombre': 'Francisco Pérez Prou',
                'telefono': '+3',
                'estado': 'activo'
               }

    # Se realiza la petición POST
    response = client.post('/admin/paciente', headers=headers, data=json.dumps(new_paciente))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Length must be between 3 and 25.' in response.json.get('telefono', '')


def test_admin_add_paciente_exists(client, auth_login_admin):
    'Prueba el endpoint /admin/paciente con un paciente existente'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo paciente
    new_paciente = {
                'username': 'user_paciente_1',
                'password': 'pass_user_paciente_1',
                'rol': 'paciente',
                'nombre': 'Jesús Gómez Narro',
                'telefono': '+34 670 89 54 32',
                'estado': 'activo'
               }

    # Se realiza la petición POST
    response = client.post('/admin/doctor', headers=headers, data=json.dumps(new_paciente))

    # Se verifica el resultado
    assert response.status_code == 409
    assert 'El usuario ya existe' in response.json.get('error', '')

def test_admin_id_paciente(client, auth_login_admin):
    'Prueba el endpoint /admin/paciente/<int:id_paciente>'

    # Se asigna un id al id_paciente
    id_paciente = 1
    # Se formatea la url con el id_paciente
    url = f'/admin/paciente/{id_paciente}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }

    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200

    user_data = json.loads(response.data)

    assert 'estado' in user_data['Paciente']
    assert 'nombre' in user_data['Paciente']
    assert user_data['Paciente']['estado'] == 'activo'
    assert user_data['Paciente']['nombre'] == 'Jesús Gómez Narro'


def test_admin_id_paciente_failed(client, auth_login_admin):
    'Prueba el fallo del endpoint /admin/paciente/<int:id_paciente>'

    # Se asigna un id 'no válido' al id_paciente
    id_paciente = 99
    # Se formatea la url con el id_paciente
    url = f'/admin/paciente/{id_paciente}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }

    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 404
    assert 'Paciente no encontrado' in response.json.get('error', '')


def test_admin_pacientes_default(client, auth_login_admin):
    'Prueba el endpoint /admin/pacientes con query params por defecto'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }

    # Se realiza la petición GET
    response = client.get('/admin/pacientes', headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200

    pacientes = json.loads(response.data)

    assert 'pacientes' in pacientes
    assert 'pagination' in pacientes
    assert pacientes['pagination']['current_page'] == 1
    assert pacientes['pagination']['per_page'] == 10


def test_admin_pacientes_custom_page(client, auth_login_admin):
    'Prueba el endpoint /admin/pacientes con query params en la url'

    # Se asignan los query params
    query_params = {
        'page': 1,
        'per_page': 5
        }
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
        }

    # Se realiza la petición GET
    response = client.get('/admin/pacientes', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200

    pacientes = json.loads(response.data)

    assert 'pacientes' in pacientes
    assert 'pagination' in pacientes
    assert pacientes['pagination']['current_page'] == 1
    assert pacientes['pagination']['per_page'] == 5


def test_admin_pacientes_custom_page_failed(client, auth_login_admin):
    'Prueba el endpoint /admin/pacientes con query params erróneos en la url'

    # Se asignan los query params
    query_params = {
        'page': 100,
        'per_page': 20
        }
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
        }

    # Se realiza la petición GET
    response = client.get('/admin/pacientes', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200
    assert 'La pagina solicitada no contiene pacientes.' in response.json.get('error', '')

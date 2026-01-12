'''
Pruebas unitarias para verificar funciones realizadas por el endpoint /admin 
para doctores.
'''

import json


def test_admin_add_doctor(client, auth_login_admin):
    'Prueba con éxito el endpoint /admin/doctor'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }

    # Se crean los datos del nuevo usuario
    new_user = {
                'username': 'user_medico_1',
                'password': 'pass_user_medico_1',
                'rol': 'medico',
                'nombre': 'Juan Pérez Gómez',
                'especialidad': 'Ortodoncia'
               }

    # Se realiza la petición POST
    response = client.post('/admin/doctor', headers=headers, data=json.dumps(new_user))

    # Se verifica el resultado
    assert response.status_code == 201
    assert 'Usuario y Doctor registrados exitosamente' in response.json.get('message', '')


def test_admin_add_doctor_data_missing(client, auth_login_admin):
    'Prueba el endpoint /admin/doctor con datos faltantes'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo doctor
    new_user = {
                'username': 'user_medico_2',
                'password': 'pass_user_medico_2',
                'nombre': 'Antonio Lapi Sánchez',
                'especialidad': 'Periodoncia'
               }

    # Se realiza la petición POST
    response = client.post('/admin/doctor', headers=headers, data=json.dumps(new_user))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Field may not be null.' in response.json.get('rol', '')


def test_admin_add_doctor_validate_error(client, auth_login_admin):
    'Prueba el endpoint /admin/doctor con un error de validación'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo doctor
    new_user = {
                'username': 'user_medico_15',
                'password': 'pass_user_medico_15',
                'rol': 'medico',
                'nombre': 'Francisco Juan Gómez',
                'especialidad': 'Or'
               }

    # Se realiza la petición POST
    response = client.post('/admin/doctor', headers=headers, data=json.dumps(new_user))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Length must be between 3 and 30.' in response.json.get('especialidad', '')


def test_admin_add_doctor_exists(client, auth_login_admin):
    'Prueba el endpoint /admin/doctor con un doctor existente'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo doctor
    new_user = {
                'username': 'user_medico_1',
                'password': 'pass_user_medico_1',
                'rol': 'medico',
                'nombre': 'Juan Pérez Gómez',
                'especialidad': 'Ortodoncia'
               }

    # Se realiza la petición POST
    response = client.post('/admin/doctor', headers=headers, data=json.dumps(new_user))

    # Se verifica el resultado
    assert response.status_code == 409
    assert 'El usuario ya existe' in response.json.get('error', '')

def test_admin_id_doctor(client, auth_login_admin):
    'Prueba el endpoint /admin/doctor/<int:id_doctor>'

    # Se asigna un id al id_doctor
    id_doctor = 1
    # Se formatea la url con el id_doctor
    url = f'/admin/doctor/{id_doctor}'
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

    assert 'especialidad' in user_data['Doctor']
    assert 'nombre' in user_data['Doctor']
    assert user_data['Doctor']['especialidad'] == 'Ortodoncia'
    assert user_data['Doctor']['nombre'] == 'Juan Pérez Gómez'


def test_admin_id_doctor_failed(client, auth_login_admin):
    'Prueba el fallo del endpoint /admin/doctor/<int:id_doctor>'

    # Se asigna un id 'no válido' al id_doctor
    id_doctor = 127
    # Se formatea la url con el id_doctor
    url = f'/admin/doctor/{id_doctor}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }

    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 404
    assert 'Doctor no encontrado' in response.json.get('error', '')


def test_admin_username_doctor(client, auth_login_doctor):
    'Prueba el endpoint /admin/doctor/username'

    # Se asigna un username al doctor
    username = 'user_medico_1'
    # Se formatea la url con el username
    url = f'/admin/doctor/username?username={username}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_doctor}',
        'Content-Type': 'application/json'
    }

    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200

    doctor_data = json.loads(response.data)

    assert 'especialidad' in doctor_data
    assert 'nombre' in doctor_data
    assert doctor_data['especialidad'] == 'Ortodoncia'
    assert doctor_data['nombre'] == 'Juan Pérez Gómez'


def test_admin_username_doctor_failed(client, auth_login_doctor):
    'Prueba el fallo del endpoint /admin/doctor/username'

    # Se asigna un username 'no válido' al doctor
    username = 'user_medico_111'
    # Se formatea la url con el username
    url = f'/admin/doctor/username?username={username}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_doctor}',
        'Content-Type': 'application/json'
    }

    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 404
    assert 'Usuario no encontrado' in response.json.get('error', '')


def test_admin_doctores_default(client, auth_login_admin):
    'Prueba el endpoint /admin/doctores con query params por defecto'

    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }

    # Se realiza la petición GET
    response = client.get('/admin/doctores', headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200

    doctores = json.loads(response.data)

    assert 'doctores' in doctores
    assert 'pagination' in doctores
    assert doctores['pagination']['current_page'] == 1
    assert doctores['pagination']['per_page'] == 10


def test_admin_doctores_custom_page(client, auth_login_admin):
    'Prueba el endpoint /admin/doctores con query params en la url'

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
    response = client.get('/admin/doctores', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200

    doctores = json.loads(response.data)

    assert 'doctores' in doctores
    assert 'pagination' in doctores
    assert doctores['pagination']['current_page'] == 1
    assert doctores['pagination']['per_page'] == 5


def test_admin_doctores_custom_page_failed(client, auth_login_admin):
    'Prueba el endpoint /admin/doctores con query params erróneos en la url'

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
    response = client.get('/admin/doctores', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200
    assert 'La pagina solicitada no contiene doctores.' in response.json.get('error', '')

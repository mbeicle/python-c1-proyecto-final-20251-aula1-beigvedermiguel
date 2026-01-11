'''
Pruebas unitarias para verificar funciones realizadas por el endpoint /admin 
para usuarios.
'''

import json

def test_admin_add_usuario(client, auth_login_admin):
    'Prueba con éxito el endpoint /admin/usuario'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo usuario 
    new_user = {
                'username': 'user_paciente_12',
                'password': 'pass_user_paciente_12',
                'rol': 'paciente'
               }
    
    # Se realiza la petición POST
    response = client.post('/admin/usuario', headers=headers, data=json.dumps(new_user))

    # Se verifica el resultado
    assert response.status_code == 201
    assert 'Usuario registrado exitosamente' in response.json.get('message', '')


def test_admin_add_usuario_data_missing(client, auth_login_admin):
    'Prueba el endpoint /admin/usuario con datos faltantes'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo usuario 
    new_user = {
                'username': 'user_paciente_110',
                'password': 'pass_user_paciente_110'
               }
    
    # Se realiza la petición POST
    response = client.post('/admin/usuario', headers=headers, data=json.dumps(new_user))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Missing data for required field.' in response.json.get('rol', '')


def test_admin_add_usuario_validate_error(client, auth_login_admin):
    'Prueba el endpoint /admin/usuario con un error de validación'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo usuario 
    new_user = {
                'username': 'user_paciente_101',
                'password': 'pass_user_paciente_101',
                'rol': ''
               }
    
    # Se realiza la petición POST
    response = client.post('/admin/usuario', headers=headers, data=json.dumps(new_user))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Must be one of: admin, medico, secretaria, paciente.' in response.json.get('rol', '')


def test_admin_add_usuario_user_exists(client, auth_login_admin):
    'Prueba el endpoint /admin/usuario con un usuario existente'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo usuario 
    new_user = {
                'username': 'user_paciente_12',
                'password': 'pass_user_paciente_12',
                'rol': 'paciente'
               }
    
    # Se realiza la petición POST
    response = client.post('/admin/usuario', headers=headers, data=json.dumps(new_user))

    # Se verifica el resultado
    assert response.status_code == 409
    assert 'El usuario ya existe' in response.json.get('error', '')

def test_admin_id_usuario(client, auth_login_admin):
    'Prueba el endpoint /admin/usuario/<int:id_usuario>'
    
    # Se asigna un usuario al id_usuario
    id_usuario = 5
    # Se formatea la url con el id_usuario
    url = f'/admin/usuario/{id_usuario}'
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

    assert 'rol' in user_data['Usuario']
    assert 'username' in user_data['Usuario']
    assert user_data['Usuario']['rol'] == 'paciente'
    assert user_data['Usuario']['username'] == 'user_paciente_2'


def test_admin_id_usuario_failed(client, auth_login_admin):
    'Prueba el fallo del endpoint /admin/usuario/<int:id_usuario>'
    
    # Se asigna un usuario 'no válido' al id_usuario
    id_usuario = 57
    # Se formatea la url con el id_usuario
    url = f'/admin/usuario/{id_usuario}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 404
    assert 'Usuario no encontrado' in response.json.get('error', '')


def test_admin_usuarios_default(client, auth_login_admin):
    'Prueba el endpoint /admin/usuarios con query params por defecto'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET
    response = client.get('/admin/usuarios', headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200
    
    usuarios = json.loads(response.data)

    assert 'usuarios' in usuarios
    assert 'pagination' in usuarios
    assert usuarios['pagination']['current_page'] == 1
    assert usuarios['pagination']['per_page'] == 10


def test_admin_usuarios_custom_page(client, auth_login_admin):
    'Prueba el endpoint /admin/usuarios con query params en la url'
    
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
    response = client.get('/admin/usuarios', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200
    
    usuarios = json.loads(response.data)

    assert 'usuarios' in usuarios
    assert 'pagination' in usuarios
    assert usuarios['pagination']['current_page'] == 1
    assert usuarios['pagination']['per_page'] == 5


def test_admin_usuarios_custom_page_failed(client, auth_login_admin):
    'Prueba el endpoint /admin/usuarios con query params erróneos en la url'
    
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
    response = client.get('/admin/usuarios', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200
    assert 'La página solicitada no contiene usuarios.' in response.json.get('error', '')

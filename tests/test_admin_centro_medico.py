'''
Pruebas unitarias para verificar funciones realizadas por el endpoint /admin 
para los centros médicos.
'''

import json

def test_admin_add_centro_medico(client, auth_login_admin):
    'Prueba con éxito el endpoint /admin/centro_medico'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se crean los datos del nuevo centro médico 
    new_centro = {
                'nombre': 'Sonrisa Luminosa',
                'direccion': 'Calle Rosales 34 bajo, Madrid 28033'
               }
    
    #with client():
    # Se realiza la petición POST
    response = client.post('/admin/centro_medico', headers=headers, data=json.dumps(new_centro))
    
    # Se verifica el resultado
    assert response.status_code == 201
    assert 'Centro Médico registrado exitosamente' in response.json.get('message', '')


def test_admin_add_centro_medico_data_missing(client, auth_login_admin):
    'Prueba el endpoint /admin/centro_medico con datos faltantes'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo centro médico 
    new_centro = {
                'nombre': 'Sonrisa Luminosa'
               }
    
    # Se realiza la petición POST
    response = client.post('/admin/centro_medico', headers=headers, data=json.dumps(new_centro))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Missing data for required field.' in response.json.get('direccion', '')


def test_admin_add_centro_medico_validate_error(client, auth_login_admin):
    'Prueba el endpoint /admin/centro_medico con un error de validación'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo centro médico 
    new_centro = {
                'nombre': 'So',
                'direccion': 'Calle Rosales 34 bajo, Madrid 28033'
               }
    
    # Se realiza la petición POST
    response = client.post('/admin/centro_medico', headers=headers, data=json.dumps(new_centro))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Length must be between 3 and 40.' in response.json.get('nombre', '')


def test_admin_add_centro_medico_exists(client, auth_login_admin):
    'Prueba el endpoint /admin/centro_medico con un centro ya existente'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    # Se crean los datos de un nuevo centro médico 
    new_centro = {
                'nombre': 'Sonrisa Luminosa',
                'direccion': 'Calle Rosales 34 bajo, Madrid 28033'
               }
    
    # Se realiza la petición POST
    response = client.post('/admin/centro_medico', headers=headers, data=json.dumps(new_centro))

    # Se verifica el resultado
    assert response.status_code == 409
    assert 'El centro médico ya existe' in response.json.get('error', '')

def test_admin_id_centro_medico(client, auth_login_admin):
    'Prueba el endpoint /admin/centro_medico/<int:id_centro>'
    
    # Se asigna un id al id_centro
    id_centro = 1
    # Se formatea la url con el id_centro
    url = f'/admin/centro_medico/{id_centro}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200
    
    centro_data = json.loads(response.data)

    assert 'direccion' in centro_data['Centro Médico']
    assert 'nombre' in centro_data['Centro Médico']
    assert centro_data['Centro Médico']['id_centro'] == 1
    assert centro_data['Centro Médico']['nombre'] == 'Sonrisa Luminosa'


def test_admin_id_centro_medico_failed(client, auth_login_admin):
    'Prueba el fallo del endpoint /admin/centro_medico/<int:id_centro>'
    
    # Se asigna un id 'no válido' al id_centro
    id_centro = 99
    # Se formatea la url con el id_centro
    url = f'/admin/centro_medico/{id_centro}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 404
    assert 'Centro Médico no encontrado' in response.json.get('error', '')


def test_admin_centros_medicos_default(client, auth_login_admin):
    'Prueba el endpoint /admin/centros_medicos con query params por defecto'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET
    response = client.get('/admin/centros_medicos', headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200
    
    centros = json.loads(response.data)

    assert 'centros médicos' in centros
    assert 'pagination' in centros
    assert centros['pagination']['current_page'] == 1
    assert centros['pagination']['per_page'] == 5


def test_admin_centros_medicos_custom_page(client, auth_login_admin):
    'Prueba el endpoint /admin/centros_medicos con query params en la url'
    
    # Se asignan los query params
    query_params = {
        'page': 1,
        'per_page': 3
        }
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
        }
    
    # Se realiza la petición GET
    response = client.get('/admin/centros_medicos', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200
    
    centros = json.loads(response.data)

    assert 'centros médicos' in centros
    assert 'pagination' in centros
    assert centros['pagination']['current_page'] == 1
    assert centros['pagination']['per_page'] == 3


def test_admin_centros_medicos_custom_page_failed(client, auth_login_admin):
    'Prueba el endpoint /admin/centros_medicos con query params erróneos en la url'
    
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
    response = client.get('/admin/centros_medicos', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200
    assert 'La página solicitada no contiene Centros Médicos.' in response.json.get('error', '')

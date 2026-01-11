'''
Pruebas unitarias para verificar funciones realizadas por el endpoint /citas.
'''

import json

def test_citas_add_cita(client, auth_login_admin):
    'Prueba con éxito el endpoint /citas/agendar'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se crean los datos de la nueva cita 
    new_cita = {
                'fecha': '20-01-2026 10:00',
                'motivo': 'revision',
                'estado': 'activa',
                'id_usuario': '4',
                'id_paciente': '2',
                'id_doctor': '1',
                'id_centro': '1'
               }
    
    # Se realiza la petición POST
    response = client.post('/citas/agendar', headers=headers, data=json.dumps(new_cita))
    
    # Se verifica el resultado
    assert response.status_code == 201
    assert 'Cita registrada' in response.json.get('message', '')


def test_citas_add_cita_data_missing(client, auth_login_admin):
    'Prueba el endpoint /admin/doctor con datos faltantes'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se crean los datos del nuevo usuario 
    new_cita = {
                'fecha': '17-01-2026 10:00',
                'motivo': 'revision',
                'estado': '',
                'id_usuario': '29',
                'id_paciente': '17',
                'id_doctor': '3',
                'id_centro': '2'
               }
    
    # Se realiza la petición POST
    response = client.post('/citas/agendar', headers=headers, data=json.dumps(new_cita))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Length must be between 3 and 20.' in response.json.get('estado', '')


def test_citas_add_cita_validate_error(client, auth_login_admin):
    'Prueba el endpoint /citas/agendar con un error de validación'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se crean los datos del nuevo usuario 
    new_cita = {
                'fecha': '17-01-2026 10:00',
                'motivo': 'revision',
                'estado': 'activa',
                'id_usuario': '',
                'id_paciente': '17',
                'id_doctor': '3',
                'id_centro': '2'
               }
    
    # Se realiza la petición POST
    response = client.post('/citas/agendar', headers=headers, data=json.dumps(new_cita))

    # Se verifica el resultado
    assert response.status_code == 400
    assert 'Not a valid integer.' in response.json.get('id_usuario', '')


def test_citas_add_cita_exists(client, auth_login_admin):
    'Prueba el endpoint /citas/agendar con una cita ya existente'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se crean los datos del nuevo usuario 
    new_cita = {
                'fecha': '20-01-2026 10:00',
                'motivo': 'revision',
                'estado': 'activa',
                'id_usuario': '4',
                'id_paciente': '2',
                'id_doctor': '1',
                'id_centro': '1'
               }
    
    # Se realiza la petición POST
    response = client.post('/citas/agendar', headers=headers, data=json.dumps(new_cita))

    # Se verifica el resultado
    assert response.status_code == 200
    assert 'El Doctor ya tiene una cita a esa hora en esa fecha' in response.json.get('error', '')


def test_citas_consultar_id_cita(client, auth_login_paciente):
    'Prueba el endpoint /citas/consultar/<int:id_cita>'
    
    # Se asigna un id al id_cita
    id_cita = 1
    # Se formatea la url con el id_cita
    url = f'/citas/consultar/{id_cita}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_paciente}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200
    
    user_data = json.loads(response.data)

    assert 'estado' in user_data['Cita']
    assert 'motivo' in user_data['Cita']
    assert user_data['Cita']['estado'] == 'activa'
    assert user_data['Cita']['id_centro'] == 1


def test_citas_id_cita_failed(client, auth_login_paciente):
    'Prueba el fallo del endpoint /citas/consultar/<int:id_cita>'
    
    # Se asigna un id 'no válido' al id_cita
    id_cita = 127
    # Se formatea la url con el id_cita
    url = f'/citas/consultar/{id_cita}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_paciente}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET
    response = client.get(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 404
    assert 'Cita no encontrada' in response.json.get('error', '')


def test_citas_listar_citas_doctor(client, auth_login_doctor):
    'Prueba el endpoint /citas/listar_citas con query params: id_doctor'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_doctor}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET con el parámetro 'id_doctor'
    response = client.get('/citas/listar_citas?id_doctor=1', headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200
    citas = json.loads(response.data)

    assert citas['Citas'][0]['id_doctor'] == 1


def test_citas_listar_citas_fecha(client, auth_login_secre):
    'Prueba el endpoint /citas/listar_citas con query params: fecha'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_secre}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET con el parámetro 'fecha'
    response = client.get('/citas/listar_citas?fecha=20-01-2026 10:00:00', headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200
    citas = json.loads(response.data)

    assert citas['Citas'][0]['fecha'] == 'Tue, 20 Jan 2026 10:00:00 GMT'


def test_citas_listar_citas_paciente(client, auth_login_admin):
    'Prueba el endpoint /citas/listar_citas con query params: paciente'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET con el parámetro 'paciente'
    response = client.get('/citas/listar_citas?id_paciente=2', headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200
    user_citas = json.loads(response.data)
    assert 'Citas' in user_citas   
    assert user_citas['Citas'][0]['estado'] == 'activa'
    assert user_citas['Citas'][0]['id_paciente'] == 2


def test_citas_listar_citas_centro(client, auth_login_admin):
    'Prueba el endpoint /citas/listar_citas con query params: centro médico'
    
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición GET con el parámetro 'paciente'
    response = client.get('/citas/listar_citas?id_centro=1', headers=headers)

    # Se verifica el resultado
    assert response.status_code == 200
    citas = json.loads(response.data)
    
    assert citas['Citas'][0]['id_centro'] == 1


def test_citas_listar_citas_failed(client, auth_login_admin):
    'Prueba el endpoint /citas/listar_citas con query params erróneos en la url'
    
    # Se asignan los query params
    query_params = {
        'centro': 100
        }
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
        }
    
    # Se realiza la petición GET
    response = client.get('/citas/listar_citas', headers=headers, query_string=query_params)

    # Se verifica el resultado
    assert response.status_code == 200
    assert 'La consulta no contiene ningún resultado.' in response.json.get('error', '')


def test_citas_cancelar_cita_id_cita(client, auth_login_admin):
    'Prueba el endpoint /citas/cancelar(<int:id_cita>)'
    
    # Se asigna un id al id_cita
    id_cita = 1
    # Se formatea la url con el id_cita
    url = f'/citas/cancelar/{id_cita}'
    # Se preparan las cabeceras
    headers = {
        'Authorization': f'Bearer {auth_login_admin}',
        'Content-Type': 'application/json'
    }
    
    # Se realiza la petición PUT
    response = client.put(url, headers=headers)

    # Se verifica el resultado
    assert response.status_code == 201
    
    cita = json.loads(response.data)

    assert 'cita' in cita
    assert 'message' in cita
    assert cita['cita']['estado'] == 'cancelada'
    assert cita['message'] == 'Cita cancelada'

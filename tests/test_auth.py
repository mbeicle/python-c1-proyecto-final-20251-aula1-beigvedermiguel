'''
Pruebas unitarias para verificar funciones de autenticación en OdontoCare.
'''

import json
#from flask import Flask
#from flask.testing import FlaskClient
#from datetime import datetime
from jwt import decode, exceptions

from odontocare.config import Config


def test_public_endpoint_main(client):
    'Prueba el endpoint main que no necesita autenticación'

    response = client.get('/')
    assert response.status_code == 200
    assert 'Bienvenido a la API RESTful de OdontoCare' in response.json.get('message', '')


def test_login_failure(client):
    'Prueba login fallido con password incorrecta'
    response = client.post(
        '/auth/login',
        data=json.dumps({
            'username': 'user_admin',
            'password': 'contraseña_falsa',
            'rol': 'admin'}),
        content_type='application/json'
    )

    assert response.status_code == 401
    assert 'Password incorrecta' in response.json.get('error', '')


def test_login_success(client):
    'Prueba login con exito y validación de contenido del JWT'

    response = client.post(
        '/auth/login', 
        data=json.dumps({
        'username': 'user_admin',
        'password': 'pass_user_admin',
        'rol': 'admin'}),
        content_type='application/json'
    )

    assert response.status_code == 200
    assert 'token' in response.json
    assert 'expires_at' in response.json

    # Verificar que el token es válido
    token = response.json['token']
    try:
        decoded = decode(token, key=Config.JWT_SECRET_KEY, algorithms=['HS256'])
        assert decoded['sub'] == 'user_admin'
        assert 'exp' in decoded
    except exceptions.InvalidTokenError:
        assert False, "El token generado no es válido"

'''
Fichero de configuración para definir los recursos compartidos que usarán los tests
'''

import json
import pytest
from werkzeug.security import generate_password_hash

from odontocare.app import create_app
from odontocare.extensions import db
from odontocare.config import TestingConfig
from odontocare.models.usuarios import Usuario


@pytest.fixture(scope="session")
def app():
    ' crea la app con configuración de prueba'
    app = create_app(config_class=TestingConfig)

    # Configuración
    #app.config.from_object(TestingConfig)

    with app.app_context():
        # Crea todas las tablas de la DB
        db.create_all()

        # Crea el usuario administrador inicial
        admin_user = Usuario(
            username = 'user_admin',
            password = generate_password_hash('pass_user_admin', method='scrypt:32768:8:1'),
            rol = 'admin'
        )
        # Crea el usuario secretaria inicial
        secre_user = Usuario(
            username = 'user_secretaria',
            password = generate_password_hash('pass_user_secretaria', method='scrypt:32768:8:1'),
            rol = 'secretaria'
        )
        db.session.add(admin_user)
        db.session.add(secre_user)
        db.session.commit()

    yield app # Proporciona la app para las pruebas

    # limpia después de las pruebas
    with app.app_context():
        db.drop_all()
        db.session.remove() # Importante para limpiar la sesión

@pytest.fixture(scope="session")
def client(app):
    return app.test_client()

@pytest.fixture
def auth_login_admin(client):
    'Hace el login del administrador con exito y validación de contenido del JWT'

    response = client.post(
        '/auth/login', 
        data=json.dumps({
        'username': 'user_admin',
        'password': 'pass_user_admin',
        'rol': 'admin'}),
        content_type='application/json'
    )

    # Obtener el token
    token = response.json['token']

    return token

@pytest.fixture
def auth_login_secre(client):
    'Hace el login de la secretaria con exito y validación de contenido del JWT'

    response = client.post(
        '/auth/login', 
        data=json.dumps({
        'username': 'user_secretaria',
        'password': 'pass_user_secretaria',
        'rol': 'secretaria'}),
        content_type='application/json'
    )

    # Obtener el token
    token = response.json['token']

    return token

@pytest.fixture
def auth_login_paciente(client):
    'Hace el login de un paciente con exito y validación de contenido del JWT'

    response = client.post(
        '/auth/login', 
        data=json.dumps({
        'username': 'user_paciente_1',
        'password': 'pass_user_paciente_1',
        'rol': 'paciente'}),
        content_type='application/json'
    )

    # Obtener el token
    token = response.json['token']

    return token

@pytest.fixture
def auth_login_doctor(client):
    'Hace el login de un doctor con exito y validación de contenido del JWT'

    response = client.post(
        '/auth/login', 
        data=json.dumps({
        'username': 'user_medico_1',
        'password': 'pass_user_medico_1',
        'rol': 'medico'}),
        content_type='application/json'
    )

    # Obtener el token
    token = response.json['token']

    return token

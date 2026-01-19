'''
String que recoge las funciones 'login' y 'carga_registros'
'''
import os
import csv
import sys
import requests


# Ruta del fichero de datos
basedir_data = os.path.join(os.getcwd(), 'data')
FILE_CSV =os.path.join(basedir_data, 'datos_usuarios.csv')
FILE_CSV_DOCTORES = os.path.join(basedir_data, 'datos_medicos.csv')
FILE_CSV_PACIENTES = os.path.join(basedir_data, 'datos_pacientes.csv')
FILE_CSV_CLINICAS = os.path.join(basedir_data, 'datos_clinicas.csv')

BASE_URL = 'http://localhost:5001'


def login():
    '''
    Lee las credenciales del 'admin' del fichero datos.csv
    Envia petición POST de autenticación con el usuario 'admin'
    '''

    # Lee las credenciales del 'admin' del fichero datos.csv para hacer login
    try:
        with open(FILE_CSV, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            try:
                # Lee la primera línea (fila) del archivo
                first_line = next(reader)
                if len(first_line) >= 3:
                    payload = {
                                'username': first_line[0],
                                'password': first_line[1],
                                'rol': first_line[2]
                              }
                else:
                    print('Error: El archivo CSV no tiene suficientes campos en la primera línea.')
                    return None
            except StopIteration:
                print('Error: El archivo CSV está vacío.')
                return None
    except FileNotFoundError:
        print('Error: No se ha encontrado el archivo "datos_usuarios.csv".')
        sys.exit(1)

    # Cabeceras
    headers = {"Content-Type": "application/json"}

    # Hace login en la API y recibe el token
    try:
        # Enviar petición POST con credenciales JSON
        response_login = requests.post(
                                        f'{BASE_URL}/auth/login',
                                        json=payload,
                                        headers=headers,
                                        timeout=3
                                      )
        if response_login.status_code != 200:
            print(f"Error en login: {response_login.status_code} - {response_login.text}")

        data = response_login.json()
        token = data['token']

    except ConnectionError as e:
        print(f"Error de conexión: {e}")

    return token


def carga_reg(token):
    '''
    Procesa los datos del resto de archivos de datos.
    Carga los registros en la Base de Datos
    '''

    # Si la API proporciona un token válido para el admin
    if token:
        # Crea las cabeceras con el Bearer Token
        headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
                }

    # Lee los registros del fichero datos_medicos.csv para cargarlos en la base de datos
    try:
        with open(FILE_CSV_DOCTORES, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Lee el archivo (registros 'doctores')
            for i in range(0, 10):
                line = next(reader)
                # Recupera los datos del doctor
                datos_doctor = {
                                'username': line[0],
                                'password': line[1],
                                'rol': line[2],
                                'nombre': line[3],
                                'especialidad': line[4]
                                }

                # Envia los datos como JSON a la API
                respuesta = requests.post(f'{BASE_URL}/admin/doctor',
                                        json=datos_doctor,
                                        headers=headers,
                                        timeout=5
                                        )
                if respuesta.status_code != 201:
                    print(f'Error al registrar a un usuario: doctor {respuesta.json()}')
    except FileNotFoundError:
        print('Error: No se ha encontrado el archivo "datos_medicos.csv".')
        sys.exit(1)

    # Lee los registros del fichero datos_pacientes.csv para cargarlos en la base de datos
    try:
        with open(FILE_CSV_PACIENTES, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Lee el archivo (registros 'pacientes')
            for i in range(0, 20):
                line = next(reader)
                # Recupera los datos de paciente
                datos_paciente = {
                                'username': line[0],
                                'password': line[1],
                                'rol': line[2],
                                'nombre': line[3],
                                'telefono': line[4],
                                'estado': line[5]
                                }

                # Envia los datos como JSON a la API
                respuesta = requests.post(f'{BASE_URL}/admin/paciente',
                                        json=datos_paciente,
                                        headers=headers,
                                        timeout=5
                                        )
                if respuesta.status_code != 201:
                    print(f'Error al registrar a los usuarios: pacientes {respuesta.json()}')
    except FileNotFoundError:
        print('Error: No se ha encontrado el archivo "datos_pacientes.csv".')
        sys.exit(1)
    # Lee los registros del fichero datos_clinicas.csv para cargarlos en la base de datos
    try:
        with open(FILE_CSV_CLINICAS, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Lee el archivo (registros 'clínicas')
            for i in range(0, 2):
                line = next(reader)
                # Recupera los datos de centro_medico
                datos_centro_medico = {
                                'nombre': line[0],
                                'direccion': line[1]
                                }
                # Enviar los datos de centro_medico como JSON a la API
                respuesta = requests.post(f'{BASE_URL}/admin/centro_medico',
                                        json=datos_centro_medico,
                                        headers=headers,
                                        timeout=3
                                        )
                if respuesta.status_code != 201:
                    print(f'Error al registrar los Centros Médicos {respuesta.json()}')
    except FileNotFoundError:
        print('Error: No se ha encontrado el archivo "datos_clinicas.csv".')
        sys.exit(1)

    return

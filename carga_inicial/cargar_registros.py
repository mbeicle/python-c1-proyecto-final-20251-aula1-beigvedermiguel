'''
Docstring para el módulo que recoge las funciones 'login' y 'carga_registros'
'''
import os, csv, sys
import requests
from odontocare.config import basedir_data

FILE_CSV =os.path.join(basedir_data, 'datos.csv')
BASE_URL = 'http://127.0.0.1:5000'


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
                                'username': first_line[1],
                                'password': first_line[2],
                                'rol': first_line[3]
                              }
                else:
                    print('Error: El archivo CSV no tiene suficientes campos en la primera línea.')
                    return None
            except StopIteration:
                print('Error: El archivo CSV está vacío.')
                return None
    except FileNotFoundError:
        print('Error: No se ha encontrado el archivo "datos.csv".')
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
    Procesa los datos del archivo 'datos.csv'
    Carga los registros en la Base de Datos
    '''

    # Si la API proporciona un token válido para el admin
    if token:
        # Crea las cabeceras con el Bearer Token
        headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
                }

    # Lee los registros del fichero datos.csv para cargarlos en la base de datos
    try:
        with open(FILE_CSV, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            # Se salta la primera línea (registro 'admin')
            next(reader, None)           
            # Lee la segunda línea del archivo (registro 'secretaria')
            line = next(reader)
            # Recupera los datos
            datos_secretaria = {
                              'username': line[1],
                              'password': line[2],
                              'rol': line[3]
                             }
            # Enviar los datos como JSON a la API
            respuesta = requests.post(f'{BASE_URL}/admin/usuario',
                                        json=datos_secretaria,
                                        headers=headers
                                        )
            if respuesta.status_code != 201:
                    print(f'Error al registrar la secretaria {respuesta.json()}')

            # Lee las siguientes líneas del archivo (registros 'doctores')
            for i in range(0, 10):
                line = next(reader)
                # Recupera los datos del usuario
                datos_doctor = {
                                'username': line[1],
                                'password': line[2],
                                'rol': line[3],
                                'nombre': line[5],
                                'especialidad': line[6]
                                }
                
                # Envia los datos como JSON a la API
                respuesta = requests.post(f'{BASE_URL}/admin/doctor',
                                        json=datos_doctor,
                                        headers=headers
                                        )
                if respuesta.status_code != 201:
                    print(f'Error al registrar a un usuario: doctor {respuesta.json()}')

            # Lee las siguientes líneas del archivo (registros 'pacientes')
            for i in range(0, 20):
                line = next(reader)
                # Recupera los datos de usuario
                datos_paciente = {
                                'username': line[1],
                                'password': line[2],
                                'rol': line[3],
                                'nombre': line[5],
                                'telefono': line[6],
                                'estado': line[7]
                                }
                
                # Enviar los datos como JSON a la API
                respuesta = requests.post(f'{BASE_URL}/admin/paciente',
                                        json=datos_paciente,
                                        headers=headers
                                        )
                if respuesta.status_code != 201:
                    print(f'Error al registrar a los usuarios: pacientes {respuesta.json()}')

            # Lee las siguientes líneas del archivo (registros 'centros_medicos')
            for i in range(0, 2):
                line = next(reader)
                # Recupera los datos de centro_medico
                datos_centro_medico = {
                                'nombre': line[1],
                                'direccion': line[2]
                                }
                # Enviar los datos de centro_medico como JSON a la API
                respuesta = requests.post(f'{BASE_URL}/admin/centro_medico',
                                        json=datos_centro_medico,
                                        headers=headers
                                        )
                if respuesta.status_code != 201:
                    print(f'Error al registrar los Centros Médicos {respuesta.json()}')

    except FileNotFoundError:
        print('Error: No se ha encontrado el archivo "datos.csv".')
        sys.exit(1)

    return


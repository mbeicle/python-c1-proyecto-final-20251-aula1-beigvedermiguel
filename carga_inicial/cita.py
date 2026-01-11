'''
Docstring para crear_cita:
    Crea una cita médica
    Imprime en consola el JSON con la cita creada 
'''

import csv
import os
import sys
import datetime
import json
import requests

from odontocare.config import basedir_data
from odontocare.models.citas import CitaMedica

# Configuración del cliente
BASE_URL = 'http://127.0.0.1:5000'
# Ruta de datos.csv
FILE_CSV =os.path.join(basedir_data, 'datos.csv')

# Configurción de la cita
fecha_formateada = datetime.datetime.now().strftime('%d-%m-%Y %H:%M')
FECHA = fecha_formateada
MOTIVO = 'Revision periodica'
ESTADO = 'activa'
ID_USUARIO = '13'
ID_DOCTOR = '3'
ID_CENTRO = 1

def crear_cita(app, token):
    '''
    Crea una cita médica
    Imprime en consola el JSON con la cita creada
    '''

    # Si la API proporciona un token válido para el admin
    if token:
        # Crea las cabeceras con el Bearer Token
        headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
                }

    # Crea una cita médica

    # Consulta la base de datos para ver si existe la primera cita
    with app.app_context():
        if CitaMedica.query.filter_by(id_cita=1).first() is None:
            cita_registrada = False
            while not cita_registrada:
                # Lee del fichero datos.csv los datos necesarios para crear la cita
                try:
                    with open(FILE_CSV, mode='r', newline='', encoding='utf-8') as file:
                        reader = csv.reader(file)
                        # Localizar el id_paciente que se corresponde con el id_usuario
                        for fila in reader:
                            if fila[0] == ID_USUARIO:
                                ID_PACIENTE = fila[4]
                                break
                        # Recupera los datos
                        datos_cita = {
                                      'fecha': FECHA,
                                      'motivo': MOTIVO,
                                      'estado': ESTADO,
                                      'id_usuario': ID_USUARIO,
                                      'id_paciente': ID_PACIENTE,
                                      'id_doctor': ID_DOCTOR,
                                      'id_centro': ID_CENTRO
                                     }
                    # Enviar los datos como JSON a la API
                    respuesta = requests.post(f'{BASE_URL}/citas/agendar',
                                                json=datos_cita,
                                                headers=headers,
                                                timeout=3
                                                )
                    if respuesta.status_code == 201:
                        cita_registrada = True
                    else:
                        print(f'Error al registrar la cita {respuesta.json()}')
                    datos_json = respuesta.json()
                    json_output = json.dumps(datos_json, indent=4)
                    print("--- JSON de primera cita médica en consola ---")
                    print(json_output)
                    print("----------------------------------------------")
                except FileNotFoundError:
                    print('Error: No se ha encontrado el archivo "datos.csv".')
                    sys.exit(1)
        else:
            print('La cita ya existe. Omitiendo crear cita.')

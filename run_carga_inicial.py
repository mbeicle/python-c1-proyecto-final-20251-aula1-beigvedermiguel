'''
Docstring para carga_inicial: gestiona la app Flask en un subproceso 
y llama al resto de funciones. 
'''

import sys
from os import getcwd
import subprocess, time
from flask import Flask
from odontocare import config as conf
from carga_inicial import seed_admin, cargar_registros, cita

# Define el directorio de trabajo
dir_actual = getcwd()

if __name__ == '__main__':

    # Crea la aplicación Flask
    app = Flask(__name__)
    # Carga la configuración
    app.config.from_object(conf.Config)

    # Inicia el servidor Flask en un subproceso
    command = [sys.executable, dir_actual + '\\run_odontocare.py']
    print("Iniciando servidor Flask...")
    # Usamos subprocess.Popen para que el script cliente no se bloquee.
    process = subprocess.Popen(command)

    # Da tiempo al servidor para que se inicie
    print("Esperando a que el servidor se inicie...")
    time.sleep(3)

    # El script cliente continúa con el resto de operaciones

    # Añade el registro de 'admin' directamente a la Base de Datos
    seed_admin.run_seed(app)

    # Hace login con los datos de 'admin'
    token = cargar_registros.login()
    # Carga el resto de los registros del archivo csv en la Base de Datos
    cargar_registros.carga_reg(token)
    # Crea cita médica
    cita.crear_cita(app, token)

    # Cuando el script cliente termina, se cierra el servidor
    print("Finalizando servidor Flask...")
    process.terminate()
    print("Servidor Flask cerrado.")

'''
String para carga_inicial: gestiona la creación de la Base de datos 
y la llamada al resto de funciones que hacen la carga de datos inicial 
en la Base de datos. 
'''

import requests

from odontocare.app_gestion import app
from script_cliente import cargar_cita, seed_admin, cargar_registros
from servicio_gestion.extensions import db


def setup_services():
    '''
    Función que crea la base de datos e inicializa los datos 
    de la aplicación OdontoCare.
    '''
    try:
        # 1. Crea la base de datos
        with app.app_context():
            db.create_all()
        print({'message': 'Base de datos creada.'})
        # 2. Llama al script de seed_admin para crear los usuarios admin y secretaria
        seed_admin.run_seed(app)
        # 3. Hace login con los datos de 'admin'
        token = cargar_registros.login()
        # 4. Carga el resto de los registros de los archivos 'csv' en la Base de Datos
        cargar_registros.carga_reg(token)
        print('Registros de doctores, pacientes y centros médicos creados.')
        # 5. Crea la primera cita médica
        cargar_cita.crear_cita(app, token)
        print('Primera cita médica creada.')
    except requests.exceptions.ConnectionError:
        print('Error: El servicio_gestion no está corriendo.')

if __name__ == "__main__":
    setup_services()

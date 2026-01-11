'''
Docstring para el módulo que recoge la función que lee los datos del usuario 
'admin' y añade el registro a la Base de Datos.
'''

import os
import csv
import sys
from werkzeug.security import generate_password_hash

from odontocare.config import basedir_data
from odontocare.extensions import db
from odontocare.models.usuarios import Usuario

FILE_CSV =os.path.join(basedir_data, 'datos.csv')


def run_seed(app):
    '''
    Lee los datos de 'datos.csv' y añade el registro 'admin' a la Base de Datos
    '''

    # Lee las credenciales del 'admin' del fichero datos.csv
    try:
        with open(FILE_CSV, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            try:
                # Lee la primera línea (fila) del archivo
                first_line = next(reader)
                if len(first_line) >= 3:
                    username = first_line[1]
                    password = first_line[2]
                    password = generate_password_hash(password, method='scrypt:32768:8:1')
                    rol = first_line[3]
                else:
                    print('Error: El archivo CSV no tiene suficientes campos en la primera línea.')
                    return None
            except StopIteration:
                print('Error: El archivo CSV está vacío.')
                return None
    except FileNotFoundError:
        print('Error: No se ha encontrado el archivo "datos.csv".')
        sys.exit(1)

    # Graba los datos del usuario 'admin' en la Base de Datos
    with app.app_context():
        db.init_app(app)
        # Crea un usuario 'admin' si no existe
        if Usuario.query.filter_by(username=username).first() is None:
            # Crear datos iniciales de admin
            admin_user = Usuario(#id_usuario=1,
                                username=username,
                                password=password,
                                rol=rol
                                )
            # Guarda los datos en la base de datos y la cierra al terminar
            try:
                db.session.add(admin_user)
                db.session.commit()
            except:
                db.session.rollback()
                raise
            finally:
                db.session.close()
            print('Base de datos inicializada y usuario "admin" creado.')
        else:
            print('El usuario "admin" ya existe. Omitiendo seeding.')

    return

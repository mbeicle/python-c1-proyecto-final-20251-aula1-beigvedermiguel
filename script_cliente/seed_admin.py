'''
Script que recoge la función que lee los datos del usuario 'admin'
y el usuario 'secretaria' desde el fichero de datos_usuarios y añade
el registro a la Base de Datos.
'''

import os
import csv
import sys
from werkzeug.security import generate_password_hash

from servicio_gestion.extensions import db
from servicio_gestion.models.usuarios import Usuario


# Ruta del fichero de datos
basedir_data = os.path.join(os.getcwd(), 'data')
FILE_CSV =os.path.join(basedir_data, 'datos_usuarios.csv')


def run_seed(app):
    '''
    Lee los datos de 'datos_usuarios.csv' y añade los registros del 'admin'
     y la 'secretaria' a la Base de Datos.
    '''

    # Lee los datos
    try:
        with open(FILE_CSV, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            try:
                # Lee las dos líneas del archivo
                for i in range(0, 2):
                    line = next(reader)
                    # Recupera los datos
                    username = line[0]
                    password = line[1]
                    password = generate_password_hash(password, method='scrypt:32768:8:1')
                    rol = line[2]
                    # Graba los datos del usuario 'admin' en la Base de Datos
                    with app.app_context():
                        #db.init_app(app)
                        # Crea cada usuario si no existe
                        if Usuario.query.filter_by(username=username).first() is None:
                            # Crear datos iniciales de admin
                            user = Usuario(username=username,
                                           password=password,
                                           rol=rol
                                          )
                            # Guarda los datos en la base de datos y la cierra al terminar
                            try:
                                db.session.add(user)
                                db.session.commit()
                            except:
                                db.session.rollback()
                                raise
                            print('Usuarios admin y secretaria, creados.')
                        else:
                            print(f'El usuario {rol} ya existe. Omitiendo seeding.')
                with app.app_context():
                    db.session.close()
            except StopIteration:
                print('Error: El archivo CSV está vacío.')
                return None
    except FileNotFoundError:
        print('Error: No se ha encontrado el archivo "datos_usuarios.csv".')
        sys.exit(1)

    return

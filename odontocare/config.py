'''
Declara la configuración de la app 
'''

import os
from os import path, getcwd
import datetime
import enum
from dotenv import load_dotenv


# Definimos el enumerador de Python
class EstadoUsuario(enum.Enum):
    'clase enum para estados de usuario'
    ACTIVO = 'activo'
    INACTIVO = 'inactivo'

# Define el directorio de trabajo
dir_actual = getcwd()
basedir = dir_actual + '\\odontocare'
basedir_data = dir_actual + '\\data'

# Define el nombre de la carpeta para guardar la base de datos
DB_FOLDER = "database"
# Define el nombre del archivo de la base de datos
DB_FILE = "odontocare.db"

load_dotenv(path.join(dir_actual, '.env'))

class Config:
    'configuración base con variables de entorno'
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir, DB_FOLDER, DB_FILE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')
    # Configuración JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
    JWT_EXPIRATION_DELTA = datetime.timedelta(hours=12)  # Tiempo de expiración del token
    FLASK_ENV = os.getenv('FALSK_ENV')

class TestingConfig(Config):
    'configuración de testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Base de datos en memoria

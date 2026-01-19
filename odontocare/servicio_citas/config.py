'''
Declara la configuración de la app_citas 
'''

from os import path, getcwd, getenv
import enum
import datetime
from dotenv import load_dotenv

# Define el directorio de trabajo
dir_actual = getcwd()
basedir_data = dir_actual + '\\data'
basedir_db = dir_actual + '\\database'

# Carga las variables de entorno desde el archivo .env
load_dotenv(path.join(dir_actual, '.env'))

# Definimos el enumerador de Python
class EstadoUsuario(enum.Enum):
    'clase enum para estados de usuario'
    ACTIVO = 'activo'
    INACTIVO = 'inactivo'

class Config:
    'configuración base con variables de entorno'
    # Intenta leer la ruta de la base de datos desde una variable de entorno (para Docker)
    # Si no existe, usa la ruta de la carpeta local

    db_external_path = getenv('DB_PATH')
    if db_external_path:
        # Dentro de Docker, usa la ruta absoluta montada
        print(db_external_path)
        SQLALCHEMY_DATABASE_URI = 'sqlite:////app/data/odontocare.db'    #{db_external_path}'
    else:
        # Fuera de Docker, se mantiene la ruta original
        SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path.join(basedir_db, 'odontocare.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    SECRET_KEY = getenv('SECRET_KEY')
    # Configuración JWT
    JWT_SECRET_KEY = getenv('JWT_SECRET_KEY')
    JWT_EXPIRATION_DELTA = datetime.timedelta(hours=12)  # Tiempo de expiración del token
    FLASK_ENV = getenv('FALSK_ENV')

class TestingConfig(Config):
    'configuración de testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Base de datos en memoria

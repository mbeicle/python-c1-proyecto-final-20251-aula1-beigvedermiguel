'''
Script dónde se crea la aplicación principal OdontoCare (Flask), 
se leen las configuraciones, se crea la base de datos 
y se registran los blueprints.
'''

from flask import Flask

from odontocare.extensions import db
from odontocare.config import Config
from odontocare.routes import main, admin, auth, cita


DB_NAME = 'odontocare.db'

def create_app(config_class=Config):
    """
    Crea y configura la aplicación Flask
    """
    app = Flask(__name__)

    # Configuración
    app.config.from_object(config_class)
    # Indicamos a la app a qué base de datos se tiene que conectar
    db.init_app(app)
    # Creamos la base de datos
    with app.app_context():
        db.create_all()

    # Registra los Blueprints
    app.register_blueprint(main.main, url_prefix='/')
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')
    app.register_blueprint(admin.admin_bp, url_prefix='/admin')
    app.register_blueprint(cita.citas_bp, url_prefix='/citas')

    return app

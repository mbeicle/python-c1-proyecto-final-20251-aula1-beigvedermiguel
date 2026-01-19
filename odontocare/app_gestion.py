'''
Script dónde se crea el servicio de gestión de la aplicación OdontoCare, 
se leen las configuraciones, se crea la base de datos 
y se registran los blueprints.
'''

from flask import Flask

from servicio_gestion.config import Config

from servicio_gestion.extensions import db
from servicio_gestion.routes import main, auth, admin
from servicio_citas.routes import cita

app = Flask(__name__)

# Configuración
app.config.from_object(Config)
# Indicamos a la app a qué base de datos se tiene que conectar
db.init_app(app)
# Creamos la base de datos
with app.app_context():

    # Registra los Blueprints
    app.register_blueprint(main.main, url_prefix='/')
    app.register_blueprint(auth.auth_bp, url_prefix='/auth')
    app.register_blueprint(admin.admin_bp, url_prefix='/admin')
    app.register_blueprint(cita.citas_bp, url_prefix='/citas')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001) # El servicio de citas debe ir en el 5002

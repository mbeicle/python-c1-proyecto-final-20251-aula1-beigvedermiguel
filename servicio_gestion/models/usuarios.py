'''
Declaración del modelo de tabla 'usuario' para la base de datos
'''

from werkzeug.security import generate_password_hash, check_password_hash

from servicio_gestion.extensions import db


class Usuario(db.Model):
    'Define el modelo de la tabla Usuario para la base de datos'
    __tablename__ = 'usuarios'
    id_usuario = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    username = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(128), nullable=False, unique=True)
    rol = db.Column(db.String(15), nullable=False)

    def set_password(self, password):
        'genera password'
        self.password = generate_password_hash(password, method='scrypt:32768:8:1')

    def check_password(self, password):
        'compara password y password'
        return check_password_hash(self.password, password)

    def to_dict(self):
        'Serializa el usuario a diccionario/JSON para respuestas JSON'
        return {'id_usuario': self.id_usuario,
                'username': self.username, 
                'rol': self.rol
               }

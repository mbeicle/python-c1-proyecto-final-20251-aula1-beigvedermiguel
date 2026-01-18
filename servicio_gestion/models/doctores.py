'''
Declaración del modelo de tabla 'doctor' para la base de datos
'''

from servicio_gestion.extensions import db

class Doctor(db.Model):
    'Define el modelo de la tabla Doctor para la base de datos'
    __tablename__ = 'doctores'
    id_doctor = db.Column(db.Integer, primary_key=True, nullable=False,
                          unique=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'),
                           nullable=False, unique=True
                          )
    nombre = db.Column(db.String(80), nullable=False)
    especialidad = db.Column(db.String(30), nullable=False)
    # Define la relación con la tabla 'Usuario'.
    # El 'backref' permite acceder al id_doctor desde Usuarios.
    usuarios = db.relationship('Usuario', backref='doctor')

    def to_dict(self):
        'Serializa el doctor a diccionario/JSON para respuestas JSON'
        return {'id_doctor': self.id_doctor,
                'id_usuario': self.id_usuario,
                'nombre': self.nombre, 
                'especialidad': self.especialidad
               }

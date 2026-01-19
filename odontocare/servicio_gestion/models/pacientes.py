'''
Declaración del modelo de tabla 'paciente' para la base de datos
'''
from servicio_gestion.config import EstadoUsuario
from servicio_gestion.extensions import db

class Paciente(db.Model):
    'Define el modelo de la tabla Paciente para la base de datos'
    __tablename__ = 'pacientes'
    id_paciente = db.Column(db.Integer, primary_key=True, unique=True, autoincrement=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'),
                           nullable=False, unique=True
                          )
    nombre = db.Column(db.String(80), nullable=False)
    telefono = db.Column(db.String(25), nullable=False)
    estado = db.Column(db.Enum(EstadoUsuario), default=False, nullable=False)

    def to_dict(self):
        'Serializa el paciente a diccionario/JSON para respuestas JSON'
        return {'id_paciente': self.id_paciente,
                'id_usuario': self.id_usuario,
                'nombre': self.nombre, 
                'telefono': self.telefono,
                'estado': self.estado
               }

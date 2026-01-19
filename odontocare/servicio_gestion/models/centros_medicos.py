'''
Declaración de modelos de la tabla 'centro_medico' para la base de datos
'''

from servicio_gestion.extensions import db

class CentroMedico(db.Model):
    'Define el modelo de la tabla CentroMedico para la base de datos'
    __tablename__ = 'centro_medico'
    id_centro = db.Column(db.Integer, primary_key=True, nullable=False,
                          unique=True, autoincrement=True)
    nombre = db.Column(db.String(40), nullable=False, unique=True)
    direccion = db.Column(db.String(80), nullable=False, unique=True)

    def to_dict(self):
        'Serializa el centro médico a diccionario/JSON para respuestas JSON'
        return {'id_centro': self.id_centro,
                'nombre': self.nombre, 
                'direccion': self.direccion
               }

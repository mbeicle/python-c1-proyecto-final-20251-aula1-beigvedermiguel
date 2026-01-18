'''
Declaración del modelo de tabla 'cita' para la base de datos
'''

from servicio_gestion.extensions import db

class CitaMedica(db.Model):
    'Define el modelo de la tabla CitaMedica para la base de datos'
    __tablename__ = 'cita_medica'
    id_cita = db.Column(db.Integer, primary_key=True, nullable=False,
                        unique=True, autoincrement=True)
    fecha = db.Column(db.DateTime, nullable=False)
    motivo = db.Column(db.String(30))
    estado = db.Column(db.String(20))
    id_paciente = db.Column(db.Integer, db.ForeignKey('pacientes.id_paciente'),
                            nullable=False
                           )
    id_doctor = db.Column(db.Integer, db.ForeignKey('doctores.id_doctor'),
                          nullable=False
                         )
    id_centro = db.Column(db.Integer, db.ForeignKey('centro_medico.id_centro'),
                         nullable=False
                         )
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id_usuario'),
                           nullable=False
                          )
    # Relación inversa (opcional, para acceder a las citas desde el doctor)
    #doctor = db.relationship("Doctor", back_populates="cita_medica")


    def to_dict(self):
        'Serializa la cita a diccionario/JSON para respuestas JSON'
        return {'id_cita': self.id_cita,
                'fecha': self.fecha,
                'motivo': self.motivo,
                'estado': self.estado,
                'id_paciente': self.id_paciente,
                'id_doctor': self.id_doctor, 
                'id_centro': self.id_centro,
                'id_usuario': self.id_usuario
               }

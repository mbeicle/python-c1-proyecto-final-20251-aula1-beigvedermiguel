'''
Docstring para odontocare.schemas.paciente_schema
'''

from marshmallow import Schema, fields, validate
from marshmallow_enum import EnumField

from servicio_gestion.config import EstadoUsuario

# Esquema para validar los campos de Paciente
class PacienteSchema(Schema):
    'clase que define el esquema de la tabla de pacientes'
    id_usuario = fields.Integer(required=True, allow_none=False)
    nombre = fields.String(required=True,
                           allow_none=False,
                           validate=validate.Length(min=3, max=80))
    telefono = fields.String(required=True,
                             allow_none=False,
                             validate=validate.Length(min=3, max=25))
    estado = EnumField(EstadoUsuario,
                       by_value=True,
                       required=True,
                       allow_none=False)

# Instancia del esquema
pacient_schema = PacienteSchema()

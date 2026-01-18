'''
Docstring para odontocare.schemas.centro_medico_schema
'''

from marshmallow import Schema, fields, validate

# Esquema para validar los campos de Paciente
class CentroMedicoSchema(Schema):
    'clase que define el esquema de la tabla de centro médico'
    nombre = fields.String(required=True,
                           allow_none=False,
                           validate=validate.Length(min=3, max=40))
    direccion = fields.String(required=True,
                              allow_none=False,
                              validate=validate.Length(min=3, max=80))

# Instancia del esquema
centr_medico_schema = CentroMedicoSchema()

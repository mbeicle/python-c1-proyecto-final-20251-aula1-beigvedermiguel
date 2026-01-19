'''
Docstring para odontocare.schemas.cita_schema
'''

from marshmallow import Schema, fields, validate

# Esquema para validar los campos de Cita
class CitaSchema(Schema):
    'clase que define el esquema de la tabla de citas'
    fecha = fields.DateTime(required=True)
    motivo = fields.String(validate=validate.Length(min=3, max=30))
    estado = fields.String(validate=validate.Length(min=3, max=20))
    id_usuario = fields.Integer(required=True, allow_none=False)
    id_paciente = fields.Integer(required=True, allow_none=False)
    id_doctor = fields.Integer(required=True, allow_none=False)
    id_centro = fields.Integer(required=True, allow_none=False)

# Instancia del esquema
cita_medica_schema = CitaSchema()

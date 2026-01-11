'''
Docstring para odontocare.schemas.doctor_schema
'''

from marshmallow import Schema, fields, validate

# Esquema para validar los campos de Doctor
class DoctorSchema(Schema):
    id_usuario = fields.Integer(required=True, allow_none=False)
    nombre = fields.String(required=True, allow_none=False, validate=validate.Length(min=3, max=80))
    especialidad = fields.String(validate=validate.Length(min=3, max=30), required=True, allow_none=False)

# Instancia del esquema
doc_schema = DoctorSchema()

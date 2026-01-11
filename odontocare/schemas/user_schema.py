'''
Docstring para odontocare.schemas.usuario_schema
'''

from marshmallow import Schema, fields, validate

# Esquema para validar los campos de Usuario
class UserSchema(Schema):
    'clase que define el esquema de la tabla usuario'
    username = fields.String(required=True,
                             allow_none=False,
                             validate=validate.Length(min=3, max=80))
    password = fields.String(validate=validate.Length(min=1),
                             required=True,
                             allow_none=False)
    rol = fields.String(validate=validate.OneOf(['admin', 'medico', 'secretaria', 'paciente']),
                        required=True,
                        allow_none=False)

# Instancia del esquema
usuario_schema = UserSchema()

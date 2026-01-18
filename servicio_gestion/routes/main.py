'''
Endpoint para la raíz de la API 'Odontocare'.
'''

from flask import Blueprint, jsonify

# Crea una instancia de Blueprint para 'main'
main = Blueprint('main_bp', __name__)

# Define la ruta para main
@main.route('/', methods=['GET'])
def home():
    """
    Devuelve un mensaje de bienvenida y el estado de la API en formato JSON.
    """

    return jsonify({
        'status': 'success',
        'message': 'Bienvenido a la API RESTful de OdontoCare',
        'version': '1.0',
        'author': 'Miguel Beigveder',
        'endpoints': {
            'main': '/odontocare/modulos/main',
            'auth': '/odontocare/modulos/auth',
            'admin': 'odontocare/modulos/admin',
            'citas': 'odontocare/modulos/citas',
        }
    }), 200

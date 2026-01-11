'''
Script que instancia la aplicación OdontoCare e inicia el servidor
'''

from odontocare.app import create_app

# Crea la instancia de la aplicación
app = create_app()

if __name__ == '__main__':
    # Inicia el servidor de desarrollo
    app.run()

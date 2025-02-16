import os

class Seguridad:
    SECRET_KEY = '1234_567_89'

class Config (Seguridad):
    # Heredo de la clase Seguridad
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://postgres:admin@localhost/requerimientos')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


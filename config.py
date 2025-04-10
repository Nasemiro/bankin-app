import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'f6e901092faafaec5e1bd28a084592d1641e75a8210ce966e0372384d836e770')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(basedir, 'instance', 'bank.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'dc64e4d4e17e6e78c5becbf400abf2c63e49591432b5341a00f7a93a8b4c8b1e')

class ProductionConfig(Config):
    # For production, disable debug mode and set up logging
    DEBUG = False
    LOGGING_LEVEL = 'ERROR'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Heroku or production DB

class DevelopmentConfig(Config):
    # Enable debug mode for local development
    DEBUG = True
    LOGGING_LEVEL = 'DEBUG'
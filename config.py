import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f"sqlite:///{os.path.join(basedir, 'instance', 'bank.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')

class ProductionConfig(Config):
    # For production, disable debug mode and set up logging
    DEBUG = False
    LOGGING_LEVEL = 'ERROR'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')  # Heroku or production DB

class DevelopmentConfig(Config):
    # Enable debug mode for local development
    DEBUG = True
    LOGGING_LEVEL = 'DEBUG'
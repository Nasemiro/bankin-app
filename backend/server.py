from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig
from backend.extensions import db, bcrypt, migrate, jwt, cors
from backend.routes import register_routes
from backend import models

app = Flask(__name__)
app.config.from_object(DevelopmentConfig)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
migrate.init_app(app, db)
jwt.init_app(app)
cors.init_app(app)

# Register routes
register_routes(app)

if __name__ == "__main__":
    app.run(debug=True)

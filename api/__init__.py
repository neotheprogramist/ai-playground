from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from .db import db, migrate
from .config.config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure CORS
    CORS(
        app,
        resources={r"/*": {"origins": app.config['CORS_ORIGINS']}},
        allow_headers=app.config['CORS_HEADERS'],
        methods=app.config['CORS_METHODS'],
    )

    # Initialize API
    api = Api(app)

    # Import and register resources
    from .resources.session import StartSession, ResetEnv
    from .resources.environment import StepEnv
    from .resources.actions import GetActions

    # Register routes
    api.add_resource(StartSession, "/start")
    api.add_resource(StepEnv, "/step")
    api.add_resource(ResetEnv, "/reset")
    api.add_resource(GetActions, "/actions")

    return app

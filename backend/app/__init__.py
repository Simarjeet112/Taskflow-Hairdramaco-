from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    CORS(app, origins=[
        os.getenv("FRONTEND_URL", "http://localhost:3000")
    ])

    from .routes.tasks import tasks_bp
    from .routes.users import users_bp
    app.register_blueprint(tasks_bp, url_prefix="/api/tasks")
    app.register_blueprint(users_bp, url_prefix="/api/users")

    return app
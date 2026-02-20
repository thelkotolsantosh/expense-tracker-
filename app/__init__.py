from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes import expenses_bp, categories_bp, summary_bp
    app.register_blueprint(expenses_bp, url_prefix="/api/expenses")
    app.register_blueprint(categories_bp, url_prefix="/api/categories")
    app.register_blueprint(summary_bp, url_prefix="/api/summary")

    return app

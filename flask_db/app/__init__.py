from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def create_app():
    app = Flask(__name__,instance_relative_config=False)
    app.config.from_object(Config)
    db.init_app(app)

    with app.app_context():

        from .main import main_routes
        app.register_blueprint(main_routes.main_bp)

        db.Model.metadata.reflect(db.engine)

        from .dash_application import dash_example
        app = dash_example.Add_Dash(app)

        migrate=Migrate(app,db)
        return app

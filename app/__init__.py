from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from app.core.config import settings
from app.db.session import SessionLocal
from app.api.namespaces import api  # Import api from namespaces

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # CORS configuration
    CORS(app)

    # Database configuration
    app.config["SQLALCHEMY_DATABASE_URI"] = settings.DATABASE_URL
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    # Create the tables if they don't exist
    with app.app_context():
        db.create_all()

    # Initialize API
    api.init_app(app)

    # Make a SessionLocal available to all blueprints
    app.session_local = SessionLocal

    @app.teardown_appcontext
    def close_session(exception):
        db.session.close()

    return app


# Your event listeners...
@event.listens_for(db.session, "after_attach")
def on_attach(session, instance):
    """This will be called when the app is initialized."""
    if not session.app.debug:
        session.configure(expire_on_commit=False)


@event.listens_for(db.session, "after_commit")
def on_commit(session):
    """This will be called after a commit."""
    pass


@event.listens_for(db.session, "after_rollback")
def on_rollback(session):
    """This will be called after a rollback."""
    session.close()

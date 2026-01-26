from flask import Flask

def create_app():
    app = Flask(__name__)

    # Blueprints
    from app.home.routes import home_bp
    from app.projects.routes import projects_bp
    from app.contact.routes import contact_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(projects_bp, url_prefix="/projects")
    app.register_blueprint(contact_bp, url_prefix="/contact")

    return app

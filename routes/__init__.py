'''
from .auth import auth_bp
from .main import main_bp
from .catalog import catalog_bp
from .courses import courses_bp
from .users import users_bp

def register_routes(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(users_bp)
'''




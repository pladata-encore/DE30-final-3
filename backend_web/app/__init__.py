import os
from flask import Flask
from redis import Redis


redis_client = Redis(host='localhost', port=6379, db=0)


def create_app():
    app = Flask(__name__)
    app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

    from app.user import user as user_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/user')

    from app.match import match as match_blueprint
    app.register_blueprint(match_blueprint, url_prefix='/match')

    return app

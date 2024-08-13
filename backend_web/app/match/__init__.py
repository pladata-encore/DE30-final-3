from flask import Blueprint


match = Blueprint('match', __name__)

from app.match import routes

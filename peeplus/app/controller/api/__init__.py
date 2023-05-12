from flask import Blueprint
route_api = Blueprint('api_router', __name__)

from app.controller.api.user.user import *
from app.controller.api.user.event import *
from app.controller.api.user.eventCount import *

@route_api.route("/")
def index():
    return "Mina Api V1.0~~"

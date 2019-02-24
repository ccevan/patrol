from flask import Blueprint
from flask_cors import CORS

user = Blueprint('user',__name__,url_prefix='/api/v1/user',template_folder='templates')
CORS(user)
from . import gushi

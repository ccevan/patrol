from flask import Blueprint

monitor = Blueprint('monitor',__name__,url_prefix='/api/v1/monitor',template_folder='templates')

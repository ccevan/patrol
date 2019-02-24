from flask import Blueprint

dashboard = Blueprint('dashboard',__name__,url_prefix='/api/v1/dashboard',template_folder='templates')

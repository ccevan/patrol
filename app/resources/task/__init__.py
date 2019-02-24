from flask import Blueprint
from flask_cors import CORS

task = Blueprint('task',__name__, url_prefix='/api/v1/task', template_folder='templates')
CORS(task)

from . import tasks, faults
# from . import listenRedis, tasks
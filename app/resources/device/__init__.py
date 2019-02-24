from flask import Blueprint
from flask_cors import CORS

device = Blueprint('device',__name__,url_prefix='/api/v1/device',template_folder='templates')
CORS(device)

# from . import camera_platform, camera, organizations, channel
# from . import groups, camera_list
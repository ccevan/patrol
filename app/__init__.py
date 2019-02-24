import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import import_string
from config import config
from flask_session import Session
from flask_apscheduler import APScheduler
from flask_redis import FlaskRedis
import jwt
from loggings import logger
import json
# from flask_moment import Moment
# from flask_bootstrap import Bootstrap
# from flask_mail import Mail
# from flask_login import LoginManager

# mail = Mail()
# moment = Moment()
# bootstrap = Bootstrap()
# login_manager = LoginManager()
# login_manager.session_protection = "strong"
# login_manager.login_view = "devicetem.login"
db = SQLAlchemy()
csrf = CSRFProtect()
scheduler = APScheduler()
redis_store = FlaskRedis()
session = Session()
# celery = Celery(__name__,backend=baseconfig.CELERY_RESULT_BACKEND,broker=baseconfig.CELERY_BROKER_URL)

def response_tem(code,  data=None,  msg=None,  userdata=None,  **kwargs):
    """
    :param code: 返回码
    :param data: 数据列表
    :param msg: 返回说明
    :param userdata: 用户数据
    :param kwargs:
    :return:
    """

    re_json = {
        "code":  code,
        "data":  data,
        "msg":  msg,
        "userdata":  userdata
    }
    if kwargs:
        for key in kwargs:
            re_json[key] = kwargs[key]

    return json.dumps(re_json,  indent=4,  default=str,  sort_keys=True)


def create_app(config_name):
    app = Flask(__name__)
    config_mode = config[config_name]
    app.config.from_object(config_mode)
    db.init_app(app)
    redis_store.init_app(app)
    session.init_app(app)
    # scheduler.init_app(app)
    # scheduler.start()
    # csrf.init_app(app)
    # moment.init_app(app)
    # mail.init_app(app)
    # bootstrap.init_app(app)
    # celery.conf.update(app.config)
    # login_manager.init_app(app)

    filenames = os.listdir("app/resources")
    for filename in filenames:
        if os.path.isdir("app/resources/"+filename) and os.path.exists('app/resources/'+filename+'/__init__.py'):
            bp = import_string('app.resources.'+filename+':'+filename)
            app.register_blueprint(bp)

    if not scheduler.app:
        scheduler.init_app(app)
        scheduler.start()
    # @app.before_request
    # def process_token():
    #     token = request.cookies.get(
    #         'access_token',
    #         request.headers.get('Authorization', 'a.b.c'))
    #     logger.error(token)
    #     try:
    #         token = token.encode()
    #         user_info = jwt.decode(token, '40EDE6AD-C07B-4760-F68D-08D56C70ED44', audience="新系统1", algorithms=['HS256'])
    #         # return json.dumps(user_info)
    #     except jwt.ExpiredSignatureError as e:
    #         logger.error(e)
    #         # response = make_response('Your JWT has expired')
    #         code = 101
    #         msg = "Your JWT has expired"
    #         # response.status_code = 401
    #         # return response
    #         return response_tem(code=code, msg=msg)
    #
    #     except jwt.DecodeError as e:
    #         logger.error(e)
    #         # response = make_response('Your JWT is invalid')
    #         # response.status_code = 401
    #         code = 102
    #         msg = "Your JWT is invalid"
    #         return response_tem(code=code, msg=msg)

    return app, db

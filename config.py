# import os
# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.jobstores.redis import RedisJobStore

import redis
class BaseConfig(object):

    # DEBUG = True
    SECRET_KEY = "cn.com.soyuan.www"
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:soyuan@58.87.93.186:3306/patrol" # 公司测试用的
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:soyuan@127.0.0.1:3306/Patrol" # 公司测试用的
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:soyuan@172.16.102.70:3306/Patrol" # 公司测试用的
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:soyuan@58.87.93.186:3306/Patrol"  # 公司正式数据库
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:soyuan@58.87.93.186:3306/ppp"
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 是否追踪对象的修改并发送信号
    SQLALCHEMY_ECHO = True  # 记录所有发送给stderr的语句，有利于调试
    AUDIENCE = "新系统1"  # jwt的授权服务
    # REDIS_URL = "redis://:soyuan@58.87.93.186:6379/1"
    SESSION_TYPE = 'redis'  # session类型为redis
    SESSION_PERMANENT = False  # 如果设置为True，则关闭浏览器session就失效。
    SESSION_USE_SIGNER = True  # 是否对发送到浏览器上session的cookie值进行加密
    SESSION_KEY_PREFIX = 'session:'  # 保存到session中的值的前缀
    PERMANENT_SESSION_LIFETIME = 3600
    SESSION_REDIS = redis.Redis(host='58.87.93.186', port='6379', db=1, password='soyuan')

    # REDIS_URL = 'redis://172.16.20.218:6379/0'
    REDIS_URL = 'redis://127.0.0.1:6379/0'
    # REDIS_URL = 'redis://172.16.20.250:6379/0'
    ZABBIX_IP = "172.16.102.73:8080"
    ZABBIX_USERNAME = "Admin"
    ZABBIX_PASSWD = "zabbix"
    VIDEO_DIAGNOSIS_ADDRESS = "http://172.16.102.68:8009/api/v1/onlineSurveillance"

    PER_PAGE = 20
    # LISTEN_REDIS_SERVER = "172.16.101.22"
    LISTEN_REDIS_SERVER = "172.16.102.68"  # 视频质量诊断算法推送 redis
    LISTEN_REDIS_CHANNEL = "test"  # 视屏质量诊断算法订阅频道
    PLATFORM_STATUS = [0, 1]  # 0-离线  1-在线
    CAMERA_STATUS = [0, 1]  # 0-离线  1-在线
    TASK_PRIORITY = [1, 2, 3]  # 任务执行优先级  1-低 2-中 3-高
    TASK_STATUS = [0, 1, 2, 3]  # 任务的执行状态 0-未执行 1-正在执行 2-已暂停 3-已完成
    ITEM_TYPE = [1, 2, 3]  # 检测项的类型  1-视频质量 2-网络参数 3-时间校准
    FAULT_STATUS = [0, 1, 2, 3]  # 告警信息状态 0-未处理 1-已处理 2-以忽略 3-误诊断
    ALARM_MODE = [1, 2, 3, 4]  # 1 本地报警  2 短信报警  3 邮件报警  4 微信报警
    TASK_TYPE = [1, 2, 3, 4]  # 1-一次执行 2-每天执行 3-每周之行 4-每月执行
    FAULT_TYPE = [1, 2, 3]  # 1 画面异常  2 网络异常  3 时间异常

    # JOBS = [
    #     {
    #         "id": "job111",
    #         "func": "app.resources.video.jobs:my_job",
    #         "args": (1, 2),
    #         "trigger": "interval",
    #         "seconds": 3,
    #         "replace_existing": True
    #     }
    # ]

    # url="sqlite:///jobs.sqlite"
    # url="redis://:soyuan@58.87.93.186:6379/2"

    # SCHEDULER_JOBSTORES = {
    #     "default": RedisJobStore(db=2)
    # }

    SCHEDULER_EXECUTORS = {
        "default": {"type": "threadpool", "max_workers": 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        "coalesce": False,  # 累计任务是否执行,true 不执行 false执行
        "max_instances": 1  # 同一个任务在线程池中跑的最多的任务
    }

    SCHEDULER_API_ENABLED = True


config = {
    "baseConfig": BaseConfig,
}

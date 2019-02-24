import redis
import json
from loggings import logger
from app.models.models import Fault, Channel, FaultItemRelationship, Item
from multiprocessing import Process
from config import BaseConfig
from app import db


def publish_redis(host, channel, message, password=None):
    """
    push content to redis-server
    :param host: redis-server address
    :param channel: redis-server channel
    :param password: redis-server password
    :param message: what content you want to push, int or string/json
    :return: true is push successful,false is fail
    """
    returns = [True, False]
    try:
        if password:
            r = redis.Redis(host=host, password=password)
        else:
            r = redis.Redis(host=host)
        r.publish(channel, message=message)
        code = 0
    except Exception as e:
        logger.error(e)
        code = 1

    return returns[code]


def subscrib_redis(host, channel, password=None):
    """
    subscrib redis channel and listen it
    :param host: redis-server host
    :param channel: redis-server channel
    :param password: redis-server password
    :return:
    """

    try:
        if password:
            r = redis.Redis(host=host, password=password)
        else:
            r = redis.Redis(host=host)
        p = r.pubsub()
        p.subscribe([channel])

        for sub in p.listen():
            if sub["type"] == "message" or sub["type"] == "pmessage":
                channel = sub["channel"].decode()  # channel and data are both byte's data
                data = json.loads(sub["data"].decode())  # dict 类型的数据
                logger.error(data)
                if channel == "test" and type(data) is dict:

                    user_data = data.get("userData", None)  # userData now is str
                    user_data = json.loads(user_data)  # userData now is dict
                    pic_url = data.get("pictureUri", None)
                    task_id = user_data.get("taskId", None)

                    type1 = True
                    result = data.get("result", None)
                    is_Online = result.get("isOnline", 0)
                    # if not is_Online:
                    #     continue  # 如果该设备不在线, 不写入数据库

                    channel_id = result.get("cameraId", None)
                    item_list = ["fuzziness", "occlusion", "signal", "frozen",
                                 "content", "brightness", "crossGrain", "rollScreen",
                                 "chromaticColor", "noise", "dark"]
                    item_dict = {}
                    for item_name in item_list:
                        if result[item_name]["isDetect"]:
                            item_dict[item_name] = result[item_name]["value"]
                    logger.error("item_dict: {}".format(item_dict))

                    # if len(task_id) == 32 and len(channel_id) == 36:
                    if task_id and channel_id:
                        # channel_obj = Channel.query.filter_by(is_delete=False, channel_id=channel_id).first()
                        param_info = {
                            "pic_url": pic_url,
                            # "camera_id": channel_obj.device_id,
                            "channel_id": channel_id,
                            "task_id": task_id,
                            "type1": type1
                        }
                        rels = []
                        fault = Fault(**param_info)
                        for k, v in item_dict.items():
                            item_obj = Item.query.filter_by(item_name=k).first()
                            rels.append(FaultItemRelationship(fault_id=fault.id, item_id=item_obj.id, threshold= v))
                        logger.error("rels: {}".format(rels))

                        fault.items = rels
                        db.session.add(fault)
                        db.session.commit()

    except Exception as e:
        logger.error(e)


# host = "127.0.0.1"
host = BaseConfig.LISTEN_REDIS_SERVER
channel = BaseConfig.LISTEN_REDIS_CHANNEL

from app import create_app


def run_listen_redis(app=None):
    app = app or create_app("baseConfig")[0]

    with app.app_context():

        p = Process(target=subscrib_redis, args=(host, channel))
        p.start()

# message = {
#     "name":"常浩",
#     "age": 20
# }
# message = json.dumps(message)
# print(publish_redis("127.0.0.1", "test1", message))

import uuid
import json
import time
import urllib
import datetime
import threading
from app import db
from app import scheduler
from app import create_app
from loggings import logger
from app import redis_store
from pyzabbix import ZabbixAPIException
from app.resources.task.zabbix import AssignZabbixTask

from app.models.models import Task, Fault, Channel

app, _ = create_app('baseConfig')

zabbix = AssignZabbixTask()
zabbix.init_app(app)


class TaskStartHelper():
    """
    负责执行任务：调用zabbix接口，进行网络诊断，调用视频质量诊断服务。
    使用redis的队列用于添加任务缓冲，使用三个队列用于不同的优先级。
    """

    def __init__(self):
        self.video_diagnosis_url = app.config["VIDEO_DIAGNOSIS_ADDRESS"]
        self.redis_subscribe_url = "redis://" + \
                                   app.config.get("LISTEN_REDIS_SERVER") + \
                                   ":6379/" + app.config.get("LISTEN_REDIS_CHANNEL") + \
                                   '/sub'  # 初始化zabbix

        # p1 = Process(target=self.start_call_api,args=())
        # p1.start()
        t1 = threading.Thread(target=self.start_call_api, args=())
        t1.setDaemon(True)
        t1.start()

    def start_call_api(self):
        # 从redis中获取data 调用api
        logger.info("启动redis 任务监听进程。")
        while True:
            ret = redis_store.brpop(["task_high", "task_middle", "task_low"])
            data = ret[1]
            logger.info("从redis中获取视频诊断任务: {}.".format(data))
            try:
                res = self.call_api(data)  # 调用api
            except Exception as e:
                # print("****", e)
                logger.critical("视频诊断接口调用错误: {}".format(e))
                continue

            if res['code'] == 1:  # api调用成功
                # print("***** success")
                logger.info("视频诊断接口调用成功:{}".format(data))
                pass

            elif res["code"] == -10000:  # 失败：线程饱和
                logger.warning("视频诊断服务，线程饱和。")
                while True:
                    time.sleep(1)
                    res = self.call_api(data)
                    if res['code'] == 1:
                        break
            else:
                # print("video diagnosis api call error, code: {}".format(res["code"]))
                logger.error("视频诊断接口调用失败，错误码:{}, data:{}".format(res["code"], data))

    def call_api(self, data):
        req = urllib.request.Request(self.video_diagnosis_url, data=data,
                                     headers={'content-type': 'application/json'})

        response = urllib.request.urlopen(req)
        res = response.read().decode()
        res = json.loads(res)
        return res

    def network_diagnosis(self, task_id, camera_list, loss=None, delay=None, minutes=1):
        """
        启动网络诊断
        """
        try:
            if zabbix.exist(task_id):  # 重新添加zabbix, 防止数据库已经修改。
                zabbix.delete(task_id)  # TODO
                # zabbix.start(task_id)
            else:
                pass
            zabbix.add(task_id, delay=delay, loss=loss, camera_list=camera_list)

        except ZabbixAPIException as e:
            logger.error("zabbix网络诊断添加失败 task_id:{}, err: {}".format(task_id, e))
        else:
            # 网络诊断持续时间，默认5分钟
            finish_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            id = uuid.uuid4().hex
            scheduler.add_job(id=id, func=self.finish_network_diagnosis,
                              args=(task_id,),
                              replace_existing=True,
                              trigger='date',
                              run_date=finish_time)

            logger.info("启动zabbix网络诊断成功, task_id:{}。".format(task_id))

    @staticmethod
    def finish_network_diagnosis(task_id):
        """
        完成网络诊断,获取故障信息
        :param task_id:
        """
        problem_hosts = zabbix.problem(task_id)
        # 合并故障信息
        cameras = problem_hosts.delay + problem_hosts.loss
        # 类型：{ "b60755f55144455f88df8a633d12cd1a": 1535440059 }
        cameras_dict = dict()
        # 去重并使用最新的时间
        for each in cameras:
            timestamp = cameras_dict.get(each.clock)
            if timestamp:
                if int(each.clock) > timestamp:
                    cameras_dict[each.id] = int(each.clock)
            else:
                cameras_dict[each.id] = int(each.clock)

        logger.info("网络诊断结果task_id:{}, res: {}".format(task_id, cameras_dict))
        # 存数据库
        with app.app_context():
            try:
                for id, timestamp in cameras_dict.items():
                    fault = Fault()
                    fault.task_id = task_id
                    fault.camera_id = id
                    fault.type2 = True
                    fault.create_time = datetime.datetime.fromtimestamp(timestamp)
                    db.session.add(fault)

                db.session.commit()
                # 停用主机
                zabbix.delete(task_id)
            except Exception as e:
                logger.error("网络诊断故障存储失败task_id:{}, err:{}".format(task_id, e))

    def assign_task(self, task_id):
        """
        由任务调度器调用。对接视频质量诊断平台，和zabbix的接口
        :param task_id:
        :return:
        """
        logger.info("任务开始执行 task_id:{}".format(task_id))

        with app.app_context():
            task = Task.query.get(task_id)

            if not task or task.is_delete == True:
                logger.warning("任务执行失败，已删除或不存在。task_id: {}".format(task_id))
                return False

            self.update_task_status(task)  # 更新任务状态

            # camera_channel = db.session.query(Camera, Channel). \
            #     filter(Channel.camera_id == Camera.id,
            #            TaskChannelRelationship.channel_id == Channel.id,
            #            TaskChannelRelationship.task_id == task_id,
            #            Channel.is_delete == False
            #            ).all()

            # 获取相机信息用于视频质量诊断
            channels = Channel.query.filter_by(task_id=task_id,is_delete=False).all()
            cameraInfo = []
            for channel in channels:
                #TODO
                if channel.is_platform and channel.channel_id and channel.channel_number \
                        and channel.platform_host and channel.platform_port:
                    # 平台下的相机
                    each_info = {
                        "plateType": 1,
                        "serverName": "Channel",
                        "serverId": channel.channel_id,
                        "serverPath": channel.channel_number,
                        "serverIP": channel.platform_host,
                        "serverPort": int(channel.platform_port),
                        "userName": channel.platform_user or "",
                        "passWord": channel.platform_password or ""
                    }
                    cameraInfo.append(each_info)

                # else:
                    # IPC 或 NVR
                    # each_info = {
                    #     "plateType": 2,
                    #     "serverName": "Channel",
                    #     "serverId": channel.channel_id,
                    #     "serverPath": str(channel.channel_number) or "",
                    #     "serverIP": channel.platform_host,
                    #     "serverPort": int(channel.platform_port),
                    #     "userName": channel.platform_user,
                    #     "passWord": channel.platform_password
                    # }
                    #cameraInfo.append(each_info)

            # 任务检测项目关系表
            items_rel = task.items
            thresholds = {}  # 获取检测项目阀值信息
            for each in items_rel:
                thresholds[each.item.item_name] = each.threshold
            # 视频质量诊断算法参数。
            algorithmParam = {
                "fuzziness": thresholds.get("fuzziness") or 99,
                "occlusion": thresholds.get("occlusion") or 0,
                "signal": thresholds.get("signal") or 0,
                "frozen": thresholds.get("frozen") or 0,
                "content": thresholds.get("content") or 99,
                "brightness": thresholds.get("brightness") or 99,
                "crossGrain": thresholds.get("crossGrain") or 0,
                "rollScreen": thresholds.get("rollScreen") or 99,
                "chromaticColor": thresholds.get("chromaticColor") or 99,
                "noise": thresholds.get("noise") or 99,
                "dark": thresholds.get("dark") or 99,
                "move": thresholds.get("move") or 0,
                "shake": thresholds.get("move") or 0
            }

            video_diagnosis_data = {
                "userData": "{{\"taskId\":\"{}\",\"CheckName\":\"查验位 1\"}}".format(task_id),
                # "subscribeUrl": "redis://172.16.1.190:6379/test/sub/",
                "subscribeUrl": self.redis_subscribe_url,
                "cameraInfo": cameraInfo,
                "algorithmParam": algorithmParam
            }
            # 更新任务状态


            # 启动视频质量诊断服务
            self.video_quality_diagnosis_add_redis(video_diagnosis_data, priority=task.task_priority)

            # 获取相机信息ip用于网络检测。 {id:ip,id:ip}
            camera_ip_list = dict()

            # for camera, channel in camera_channel:
            #     camera_ip_list[camera.id] = camera.camera_ip
            # delay = thresholds.get("delay")
            # loss = thresholds.get("packetLossRate")
            # if delay or loss:
            #     self.network_diagnosis(task_id, camera_list=camera_ip_list, delay=delay, loss=loss)

            return True

    def video_quality_diagnosis_add_redis(self, data, priority=1):
        # 启动视频质量诊断，推送信息到redis队列中。
        if priority == 1:
            key = 'task_low'
        elif priority == 2:
            key = 'task_middle'
        else:
            key = 'task_high'
        data = json.dumps(data)
        redis_store.lpush(key, data)
        logger.info("视频诊断任务写入redis, data:{}".format(data))

    def update_task_status(self, task):
        # 更新任务状态。
        job = scheduler.get_job(task.id)
        if job and job.next_run_time.timestamp() > time.time():
            if task.task_status == 0:
                task.task_status = 1  # 运行中
                task.update()
        else:
            task.task_status = 3  # 已完成
            task.update()


task_helper = TaskStartHelper()


def task_job(task_id):
    task_helper.assign_task(task_id)


def auto_statistic_fault():
    url = 'http://127.0.0.1:8000/api/v1/task/tableCount'
    params = json.dumps({}).encode('utf8')
    req = urllib.request.Request(url, data=params,
                                 headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)
    res = response.read().decode()
    res = json.loads(res)
    if res['code'] != 0:
        logger.error("自动统计故障识别")
        # print(res)


scheduler.add_job(id="auto_statistic_fault",
                  func=auto_statistic_fault,
                  replace_existing=True,
                  trigger="cron",
                  second=0,
                  minute=0,
                  hour=3)
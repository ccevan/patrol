import calendar
from . import task
from app.models.models import Task, TaskCameraRelationship, Fault, FaultCount, Organization, Camera
from loggings import logger
import json
from flask import request, make_response, session
from app import db
from config import BaseConfig
import datetime
import time


def return_json(request):
    json_str = str(request.get_data(), encoding="utf-8")
    json_data = json.loads(json_str)
    return json_data


def response_tem(code, data=None, msg=None, userdata=None, **kwargs):
    """
    :param code: 返回码
    :param data: 数据列表
    :param msg: 返回说明
    :param userdata: 用户数据
    :param kwargs:
    :return:
    """

    re_json = {
        "code": code,
        "data": data,
        "msg": msg,
        "userdata": userdata
    }
    if kwargs:
        for key in kwargs:
            re_json[key] = kwargs[key]

    return json.dumps(re_json,  indent=4,  default=str,  sort_keys=True)


@task.route("/tasks", methods=["POST"])
def search_task():
    """
    Fuzzy search task execution
    模糊搜索任务的执行情况, 搜索字段searchInfo可以不填
    :return:
    """

    json_data = return_json(request)
    keywords = json_data.get("searchInfo", None)

    page = json_data.get("page", None)
    page_size = json_data.get("page_size", 10)
    user_data = json_data.get("userdata", None)
    # return str(keywords)
    if not(page and page_size):
        code = -1
        msg = "page和page_size参数必填"
        return response_tem(code=code, msg=msg, userdata=user_data)

    if type(page) is str:
        if not page.isdigit():
            code = -1
            msg = "page应该是数字类型"
            return response_tem(code=code, msg=msg, userdata=user_data)

    if type(page_size) is str:
        if not page_size.isdigit():
            code = -1
            msg = "page_size应该是数字类型"
            return response_tem(code=code, msg=msg, userdata=user_data)
    page = int(page)
    page_size = int(page_size)

    all_info = []

    try:

        if keywords and type(keywords) is not dict:
            code = -1
            msg = "搜索字段格式错误"
            return response_tem(code=code, msg=msg, userdata=user_data)

        if keywords:
            task_name = keywords.get("task_name", None)
            task_priority = keywords.get("task_priority", None)
            task_type = keywords.get("task_type", None)
            task_status = keywords.get("task_status", None)
            alarm_mode = keywords.get("alarm_mode", None)

            if (task_priority and task_priority not in BaseConfig.TASK_PRIORITY) \
                or (task_type and task_type not in BaseConfig.TASK_TYPE) \
                or (task_status and task_status not in BaseConfig.TASK_STATUS) \
                    or (alarm_mode and alarm_mode not in BaseConfig.ALARM_MODE):

                code = -1
                msg = "搜索参数格式不正确"
                return response_tem(code=code, msg=msg, userdata=user_data)

            search_param = {
                "is_delete": False,
            }

            if task_priority:
                search_param["task_priority"] = task_priority
            if task_type:
                search_param["task_type"] = task_type
            if task_status:
                search_param["task_status"] = task_status
            if alarm_mode:
                search_param["alarm_mode"] = alarm_mode

            pagination = Task.query.filter_by(**search_param).filter(
                     Task.task_name.like("%"+task_name+"%") if task_name is not None else ""
            ).paginate(page, page_size, 0)
        else:
            pagination = Task.query.filter_by(is_delete=False).paginate(page, page_size, 0)

        all_data = pagination.total
        all_page = pagination.pages
        now_page = pagination.page

        for _task in pagination.items:
            task_info = {
                "task_id": _task.id,
                "task_name": _task.task_name,
                "task_desc": _task.task_desc,
                "task_priority": _task.task_priority if _task.task_priority is not None else 1,
                "task_type": int(_task.task_type) if _task.task_type is not None else 1,
                "start_time": "{:02d}:{:02d}".format(
                    int(_task.hours) if _task.hours is not None else 0,
                    int(_task.minutes) if _task.minutes is not None else 0
                ),
                "alarm_mode": _task.alarm_mode if _task.alarm_mode is not None else 1,
                "task_status": _task.task_status if _task.task_status is not None else 0
            }
            all_info.append(task_info)
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
        all_data = None
        all_page = None
        now_page = None

    return response_tem(
        code=code,
        msg=msg,
        data=all_info,
        all_data=all_data,
        all_page=all_page,
        page=now_page,
        userdata=user_data
    )

#  统计异常的数量


@task.route("/faultCount")
def fault_count():
    """
    Query the fault type and the number of faults at the current time
    查询当前时刻的故障种类及故障数量
    :return:
    """

    all_info = []

    try:
        video_data = Fault.query.join(Camera).filter(
            Fault.type1 == True,
            Camera.is_delete == False
        ).all()
        network_data = Fault.query.join(Camera).filter(
            Fault.type2 == True,
            Camera.is_delete == False
        ).all()
        time_data = Fault.query.join(Camera).filter(
            Fault.type3 == True,
            Camera.is_delete == False
        ).all()

        video_num = len(video_data)
        network_num = len(network_data)
        time_num = len(time_data)
        data_info = {
            "video_num": video_num,
            "network_num": network_num,
            "time_num": time_num
        }

        total_camera = TaskCameraRelationship.query.group_by(TaskCameraRelationship.camera_id).all()
        total_camera = [rel for rel in total_camera if not rel.camera.is_delete]
        total_camera_num = len(total_camera)
        fault_camera = Fault.query.filter(Fault.status == 0).group_by(Fault.camera_id).all()
        fault_camera = [cam for cam in fault_camera if not cam.camera.is_delete]
        fault_camera_num = len(fault_camera)
        normal_camera_num = total_camera_num - fault_camera_num
        data_info["normal_num"] = normal_camera_num
        all_info.append(data_info)

        code = 0
        msg = "查询成功"

    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"

    return response_tem(
        code=code,
        data=all_info,
        msg=msg
    )


@task.route("/updateFaultData")
def update_fault_data():
    """
    Update fault statistics
    更新故障统计数据
    :return:
    """

    small_time = datetime.datetime.min
    year = int(time.strftime('%Y', time.localtime(time.time())))
    month = int(time.strftime('%m', time.localtime(time.time())))
    time_from = datetime.datetime(year, month, 1)
    time_to = time_from + datetime.timedelta(days=calendar.monthrange(year, month)[1])
    key = '{:d}-{:02d}'.format(year, month)

    try:

        organization_list = Organization.query.filter_by(is_delete=False).all()
        for org in organization_list:
            if org.is_delete:
                continue
            for platform in org.cameraplatforms.all():
                if platform.is_delete:
                    continue
                unique_camera = Fault.query.join(Camera).filter(
                    Fault.create_time >= time_from,
                    Fault.create_time <= time_to,
                    Camera.cameraplatform == platform
                ).group_by(Fault.camera_id).count()

                rel_camera_list = TaskCameraRelationship.query.join(Camera).filter(
                    TaskCameraRelationship.timestamp >= small_time,
                    TaskCameraRelationship.timestamp <= time_to,
                    Camera.cameraplatform == platform
                ).group_by(TaskCameraRelationship.camera_id).all()
                all_camera = 0  # 摄像机总数
                for rel in rel_camera_list:
                    if not rel.camera.is_delete:
                        all_camera += 1

                if all_camera == 0:
                    rate = 0  # 本月故障率
                else:
                    rate = int(float('%.2f' % (unique_camera / all_camera)) * 100)

                rel_task_list = TaskCameraRelationship.query.join(Camera).filter(
                    TaskCameraRelationship.timestamp >= small_time,
                    TaskCameraRelationship.timestamp <= time_to,
                    Camera.cameraplatform == platform
                ).group_by(TaskCameraRelationship.task_id).all()
                task_num = 0  # 本月任务总数
                for rel in rel_task_list:
                    if not rel.task.is_delete:
                        task_num += rel.task.run_num if rel.task.run_num is not None else 0
                camera_list = [rel.camera_id for rel in rel_camera_list if not rel.camera.is_delete]
                fault_list = Fault.query.filter(
                    Fault.create_time >= time_from,
                    Fault.create_time <= time_to
                ).all()
                fault_list = [f for f in fault_list if f.camera_id in camera_list]
                processed_num = 0
                misdiagnosis_num = 0
                ignore_num = 0
                unprocessed_num = 0
                for f in fault_list:
                    if f.status == 0:
                        unprocessed_num += 1
                    elif f.status == 1:
                        processed_num += 1
                    elif f.status == 2:
                        ignore_num += 1
                    elif f.status == 3:
                        misdiagnosis_num += 1

                fault_counts = FaultCount.query.filter_by(
                    date=key,
                    organization=org,
                    cameraplatform=platform
                ).first()
                if fault_counts:
                    fault_counts.num = unique_camera
                    fault_counts.rate = rate
                    fault_counts.work_num = task_num
                    fault_counts.processed = processed_num
                    fault_counts.unprocessed = unprocessed_num
                    fault_counts.ignore = ignore_num
                    fault_counts.misdiagnosis = misdiagnosis_num
                    db.session.add(fault_counts)
                else:
                    fault_param = {
                        "date": key,
                        "num": unique_camera,
                        "rate": rate,
                        "work_num": task_num,
                        "processed": processed_num,
                        "misdiagnosis": misdiagnosis_num,
                        "ignore": ignore_num,
                        "unprocessed": unprocessed_num,
                        "organization": org,
                        "cameraplatform": platform
                    }
                    new_fault = FaultCount(**fault_param)
                    db.session.add(new_fault)

            unique_camera = Fault.query.join(Camera).filter(
                Fault.create_time >= time_from,
                Fault.create_time <= time_to,
                Camera.organization == org
            ).group_by(Fault.camera_id).count()

            rel_camera_list = TaskCameraRelationship.query.join(Camera).filter(
                TaskCameraRelationship.timestamp >= small_time,
                TaskCameraRelationship.timestamp <= time_to,
                Camera.organization == org
            ).group_by(TaskCameraRelationship.camera_id).all()
            all_camera = 0  # 摄像机总数
            for rel in rel_camera_list:
                if not rel.camera.is_delete:
                    all_camera += 1

            if all_camera == 0:
                rate = 0  # 本月故障率
            else:
                rate = int(float('%.2f' % (unique_camera / all_camera)) * 100)

            rel_task_list = TaskCameraRelationship.query.join(Camera).filter(
                TaskCameraRelationship.timestamp >= small_time,
                TaskCameraRelationship.timestamp <= time_to,
                Camera.organization == org
            ).group_by(TaskCameraRelationship.task_id).all()
            task_num = 0  # 本月任务总数
            for rel in rel_task_list:
                if not rel.task.is_delete:
                    task_num += rel.task.run_num if rel.task.run_num is not None else 0
            camera_list = [rel.camera_id for rel in rel_camera_list if not rel.camera.is_delete]
            fault_list = Fault.query.filter(
                Fault.create_time >= time_from,
                Fault.create_time <= time_to
            ).all()
            fault_list = [f for f in fault_list if f.camera_id in camera_list]
            processed_num = 0
            misdiagnosis_num = 0
            ignore_num = 0
            unprocessed_num = 0
            for f in fault_list:
                if f.status == 0:
                    unprocessed_num += 1
                elif f.status == 1:
                    processed_num += 1
                elif f.status == 2:
                    ignore_num += 1
                elif f.status == 3:
                    misdiagnosis_num += 1

            fault_counts = FaultCount.query.filter_by(
                date=key,
                organization=org,
                cameraplatform=None
            ).first()
            if fault_counts:
                fault_counts.num = unique_camera
                fault_counts.rate = rate
                fault_counts.work_num = task_num
                fault_counts.processed = processed_num
                fault_counts.unprocessed = unprocessed_num
                fault_counts.ignore = ignore_num
                fault_counts.misdiagnosis = misdiagnosis_num
                db.session.add(fault_counts)
            else:
                fault_param = {
                    "date": key,
                    "num": unique_camera,
                    "rate": rate,
                    "work_num": task_num,
                    "processed": processed_num,
                    "misdiagnosis": misdiagnosis_num,
                    "ignore": ignore_num,
                    "unprocessed": unprocessed_num,
                    "organization": org,
                }
                new_fault = FaultCount(**fault_param)
                db.session.add(new_fault)

        unique_camera = (
            db.session.query(Fault.camera_id).filter(
                Fault.create_time >= time_from,
                Fault.create_time <= time_to
            ).group_by(Fault.camera_id).count()
        )

        rel_task_list = TaskCameraRelationship.query.join(Camera).filter(
            TaskCameraRelationship.timestamp >= small_time,
            TaskCameraRelationship.timestamp <= time_to,
        ).group_by(TaskCameraRelationship.task_id).all()

        rel_camera_list = TaskCameraRelationship.query.join(Camera).filter(
            TaskCameraRelationship.timestamp >= small_time,
            TaskCameraRelationship.timestamp <= time_to,
        ).group_by(TaskCameraRelationship.camera_id).all()

        all_camera = 0  # 摄像机总数
        for rel in rel_camera_list:
            if not rel.camera.is_delete:
                all_camera += 1

        if all_camera == 0:
            rate = 0
        else:
            rate = int(float('%.2f' % (unique_camera / all_camera)) * 100)

        task_num = 0  # 本月任务总数
        for rel in rel_task_list:
            if not rel.task.is_delete:
                task_num += rel.task.run_num if rel.task.run_num is not None else 0

        fault_list = Fault.query.filter(
            Fault.create_time >= time_from,
            Fault.create_time <= time_to
        ).all()

        processed_num = 0
        misdiagnosis_num = 0
        ignore_num = 0
        unprocessed_num = 0
        for f in fault_list:
            if f.status == 0:
                unprocessed_num += 1
            elif f.status == 1:
                processed_num += 1
            elif f.status == 2:
                ignore_num += 1
            elif f.status == 3:
                misdiagnosis_num += 1

        fault_counts = FaultCount.query.filter_by(date=key, organization_id=None, cameraplatform_id=None).first()
        if fault_counts:
            fault_counts.num = unique_camera
            fault_counts.rate = rate
            fault_counts.work_num = task_num
            fault_counts.processed = processed_num
            fault_counts.unprocessed = unprocessed_num
            fault_counts.ignore = ignore_num
            fault_counts.misdiagnosis = misdiagnosis_num
            db.session.add(fault_counts)
        else:
            fault_param = {
                "date": key,
                "num": unique_camera,
                "rate": rate,
                "work_num": task_num,
                "processed": processed_num,
                "misdiagnosis": misdiagnosis_num,
                "ignore": ignore_num,
                "unprocessed": unprocessed_num,
            }
            new_fault = FaultCount(**fault_param)
            db.session.add(new_fault)
        db.session.commit()

        code = 0
        msg = "数据更新成功"
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        code = -1
        msg = "数据更新失败"
    return response_tem(
        code=code,
        msg=msg
    )


@task.route("/faultNumRate")
def show_num_rate():
    """
    Demonstrate the number of failures and failure rates of the camera
    展示摄像机的故障数和故障率
    :return:
    """
    all_info = []
    try:
        fault_data = FaultCount.query.filter(FaultCount.organization_id == None, FaultCount.cameraplatform_id == None).all()
        for fault in fault_data:
            fault_list = []

            date = fault.date
            num = fault.num
            rate = fault.rate
            fault_list.append(date)
            fault_list.append(num)
            fault_list.append(rate)
            all_info.append(fault_list)

        code = 0
        msg = "查询成功"

    except Exception as e:
        db.session.rollback()
        logger.error(e)
        code = -1
        msg = "查询失败"
    return response_tem(
        code=code,
        msg=msg,
        data=all_info
    )


@task.route("/tableCount", methods=["POST"])
def search_faults():
    """
    Fuzzy search fault information
    模糊搜索故障信息, 可以根据组织机构,也可以根据相机平台
    :return:
    """
    json_data = return_json(request)
    keywords = json_data.get("searchInfo", None)
    user_data = json_data.get("userdata", None)

    all_info = []

    try:

        if keywords and type(keywords) is not dict:
            code = -1
            msg = "搜索字段格式错误"
            return response_tem(code=code, msg=msg, userdata=user_data)

        if keywords:
            organization_id = keywords.get("organization_id", None)
            platform_id = keywords.get("cameraplatform_id", None)

            if not organization_id:
                code = -1
                msg = "组织机构id不能为空"
                return response_tem(code=code, msg=msg, userdata=user_data)

            param_info = {
                "organization_id": organization_id,
                "cameraplatform_id": None
            }
            if platform_id:
                param_info["cameraplatform_id"] = platform_id

            fault_data = FaultCount.query.filter_by(**param_info).order_by(FaultCount.date.asc()).all()

        else:

            fault_data = FaultCount.query.filter(
                FaultCount.organization_id==None,
                FaultCount.cameraplatform_id==None).order_by(FaultCount.date.asc()).all()

        for fault in fault_data:
            info = []
            info.append(fault.date)
            info.append(fault.num)
            info.append(fault.rate)
            info.append(fault.work_num)
            info.append(fault.processed)
            info.append(fault.misdiagnosis)
            info.append(fault.ignore)
            info.append(fault.unprocessed)

            all_info.append(info)
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        db.session.rollback()
        code = -1
        msg = "查询失败"
    return response_tem(
        code=code,
        msg=msg,
        data=all_info,
        userdata=user_data
    )


# @task.route("/ceshi")
# def ceshi():
#     """
#     测试专用
#     :return:
#     """
#     name = request.cookies.get("passw", None)
#     print(name)
#     info = {
#         "name": "changhao",
#         "age": 18
#     }
#     info = json.dumps(info)
#     ret = make_response(info)
#     ret.set_cookie("passw", "23df2")
#     # ret.set_cookie("passw", "", expires=0)
#     session["chang"] = "hao"
#     print(session.get("chang"))
#     from app import redis_store
#     redis_store.setex("hello", 50, "hao")
#     print(redis_store.get("hello").decode())
#     return ret

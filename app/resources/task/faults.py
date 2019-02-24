"""
时间：2018年8月23日
作者：高静
功能：故障信息展示接口
"""


import json
import logging
import logging.config
from flask import request
from loggings import logger
from . import task
from sqlalchemy import desc, asc
from config import BaseConfig
from app.models.models import Fault, Channel, Task, FaultItemRelationship
from app import db


def return_json(request):
    json_str = str(request.get_data(), encoding="utf-8")
    json_data = json.loads(json_str)
    return json_data


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


def converse_int(s, default):
    if isinstance(s, int):
        return s
    if s is None:
        return default
    if isinstance(s, str):
        if s.isdigit():
            s = int(s)
            return s
        return default


# 1.查询故障信息
# URL: https://ip:port/api/v1/task/searchFault
# Method: POST
@task.route("/searchFault", methods=["POST"])
def search_fault():
    logger.info("收到查询故障信息命令")
    json_data = return_json(request)
    keywords = json_data.get("searchInfo", None)

    page_size = json_data.get("page_size", None)
    page = json_data.get("page", None)
    user_data = json_data.get("userdata")

    page = converse_int(page, None)
    page_size = converse_int(page_size, None)

    if not(page and page_size):
        code = -1
        msg = "page和page_size无效"
        return response_tem(code=code, msg=msg, userdata=user_data)

    data_list = list()

    try:

        filter = list()
        filter.append(Fault.is_delete == False)

        sort_order = 0

        if not isinstance(keywords, dict):
            return response_tem(code=-1, msg="searchInfo 格式不正确")

        if keywords:
            # channel_name = keywords.get("channel_name", None)
            task_name = keywords.get("task_name", None)
            organization_id = keywords.get("organization_id", None)
            cameraplatform_id = keywords.get("cameraplatform_id", None)
            status = keywords.get("status", None)  # 0未处理1已处理2已忽略3误诊断
            fault_type = keywords.get("fault_type", None)  # 1视频质量2网络参数3时间校准
            sort_order = keywords.get("sort_order", 0)

            sort_order = converse_int(sort_order, 0)

            status = converse_int(status, None)
            fault_type = converse_int(fault_type, None)

            if status or status == 0:
                filter.append(Fault.status == status)
            if fault_type == 1:
                filter.append(Fault.type1 == True)
            if fault_type == 2:
                filter.append(Fault.type2 == True)
            if fault_type == 3:
                filter.append(Fault.type3 == True)
            if task_name:
                filter.append(Task.task_name.like("%" + task_name + "%"))
            if organization_id:
                filter.append(Channel.organization_id == organization_id)
            if cameraplatform_id:
                filter.append(Channel.cameraplatform_id == cameraplatform_id)

        if sort_order == 1:
            sort_order = asc
        else:
            sort_order = desc
        sort_filter = [sort_order(Fault.create_time)]

        pagination = Fault.query.join(Channel, Fault.channel_id == Channel.channel_id).distinct(). \
            join(Task, Fault.task_id == Task.id).filter(*filter).order_by(*sort_filter). \
            paginate(page, per_page=page_size, error_out=False)
            # filter(*filter).order_by(*sort_filter). \

        # else:
            # pagination = Fault.query.join(Channel, Fault.channel_id == Channel.channel_id). \
            #     join(Task, Fault.task_id == Task.id). \
            #     filter(*filter).order_by(Fault.create_time.desc()). \
            #     paginate(page, per_page=page_size, error_out=False)
            # pagination = Fault.query.join(Channel, Fault.channel_id == Channel.channel_id). \
            #     join(Task, Fault.task_id == Task.id). \
            #     filter(*filter).order_by(Fault.create_time.desc()). \
            #     paginate(page, per_page=page_size, error_out=False)

        faultinfo_list = pagination.items
        all_data = pagination.total
        all_page = pagination.pages
        now_page = pagination.page

        for faultinfo in faultinfo_list:
            type_list = list()
            if faultinfo.type1:
                type_list.append(1)
            if faultinfo.type2:
                type_list.append(2)
            if faultinfo.type3:
                type_list.append(3)
            channel_obj = Channel.query.filter_by(is_delete=False, channel_id=faultinfo.channel_id, task_id=faultinfo.task_id).first()
            task_obj = Task.query.filter_by(is_delete=False, id=faultinfo.task_id).first()
            fault_dict = {
                # "fault_id": faultinfo.id,
                # # "channel_name": faultinfo.channel.channel_name if faultinfo.channel_id is not None else "",
                # "channel_number": faultinfo.channel.channel_number if faultinfo.channel_id is not None else "",
                # "task_name": faultinfo.task.task_name if faultinfo.task_id is not None else "",
                # "device_name": faultinfo.camera.camera_name if faultinfo.camera_id is not None else "",
                # "organization_name": faultinfo.camera.organization.organization_name if faultinfo.camera_id is not None else "",
                # "camera_platform_name": faultinfo.camera.cameraplatform.camera_platform_name \
                #     if faultinfo.camera.cameraplatform_id is not None else "",
                # "fault_time": faultinfo.create_time.strftime("%Y-%m-%d %H:%M:%S") if faultinfo.create_time is not None else "",
                # "status": faultinfo.status,
                # "fault_type": type_list
                "fault_id": faultinfo.id,
                "channel_id": channel_obj.channel_id if channel_obj is not None else "",
                "channel_number": channel_obj.channel_number if channel_obj.channel_number is not None else "",
                "task_name": task_obj.task_name if task_obj is not None else "",
                "device_id": channel_obj.device_id if channel_obj is not None else "",
                "organization_id": channel_obj.organization_id if channel_obj is not None else "",
                "platform_id": channel_obj.platform_id if channel_obj is not None else "",
                "fault_time": faultinfo.create_time.strftime(
                    "%Y-%m-%d %H:%M:%S") if faultinfo.create_time is not None else "",
                "status": faultinfo.status,
                "fault_type": type_list
            }
            data_list.append(fault_dict)
        code = 0
        msg = "查询成功"
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        code = -1
        msg = "查询失败"
        all_data = None
        all_page = None
        now_page = None
    return response_tem(
        code=code,
        data=data_list,
        msg=msg,
        all_data=all_data,
        all_page=all_page,
        page=now_page,
        userdata=user_data
    )


@task.route("/searchFaultDetails", methods=["POST"])
def search_fault_details():
    json_data = return_json(request)
    logger.info("收到的json是:{}".format(str(json_data)))
    fault_id = json_data.get("fault_id",None)
    userdata = json_data.get("userdata", None)
    logger.info((fault_id, userdata))

    all_info = []
    try:
        fault_info = Fault.query.filter(Fault.id == fault_id, Fault.is_delete==False).first()
        fault_item_list = FaultItemRelationship.query.filter(FaultItemRelationship.fault_id == fault_id).all()

        type_list = list()
        fault_list = list()
        if fault_info.type1:
            type_list.append(1)
        if fault_info.type2:
            type_list.append(2)
        if fault_info.type3:
            type_list.append(3)
        for fault_item_info in fault_item_list:
            fault_list.append(fault_item_info.item.item_name)

        channel_obj = Channel.query.filter_by(is_delete=False, channel_id=fault_info.channel_id).first()
        info = {
            "pic_url": fault_info.pic_url,
            "channel_id": fault_info.channel_id if fault_info is not None else "",
            "device_id": channel_obj.device_id if channel_obj is not None else "",
            "fault_type": type_list,
            "fault_list": fault_list,
            "fault_time": fault_info.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": fault_info.status
        }
        all_info.append(info)

        code = 0
        msg = "查询成功"
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        code = -1
        msg = "查询失败"
    return response_tem(
        code=code,
        msg=msg,
        data=all_info,
        userdata=userdata
    )


@task.route("/updateFaultState", methods=["POST"])
def update_fault_status():

    json_data = return_json(request)
    fault_id = json_data.get("fault_id", None)
    status = json_data.get("status", None)
    userdata = json_data.get("userdata", None)

    try:
        fault_info = Fault.query.filter(Fault.id == fault_id, Fault.is_delete==False).first()
        if status not in BaseConfig.FAULT_STATUS:
            code = -1
            msg = "故障状态参数错误1-已处理,2-忽略"
            return response_tem(code=code, msg=msg, userdata=userdata)
        if fault_info:
            fault_info.status = status
            fault_info.update()
            code = 0
            msg = "更新成功"
        else:
            logger.error("未查询到对应故障信息")
            code = -1
            msg = "未查询到对应故障信息"
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        db.session.rollback()
        code = -1
        msg = "更新失败"

    logger.info("更新故障处理状态成功")
    return response_tem(
        code=code,
        msg=msg,
        userdata=userdata)


@task.route("/deleteFault", methods=["POST"])
def delete_fault():

    json_data = return_json(request)
    fault_ids = json_data.get("fault_ids", None)
    userdata = json_data.get("userdata", None)
    if type(fault_ids) is not list:
        code = -1
        msg = "fault_ids参数不合法,应为list类型"
        return response_tem(
            code=code,
            msg=msg,
            userdata=userdata
        )

    try:
        for fault_id in fault_ids:
            fault_info = Fault.query.filter(Fault.id == fault_id, Fault.is_delete==False).first()
            if fault_info:
                fault_info.is_delete = True
                db.session.add(fault_info)
            else:
                logger.error("未查询到对应故障信息:{}".format(fault_id))
                code = -1
                msg = "未查询到对应故障信息:{}".format(fault_id)
                return response_tem(code=code, msg=msg, userdata=userdata)
        db.session.commit()
        code = 0
        msg = "删除成功"
    except Exception as e:
        # 接口调用失败
        logger.error(e)
        db.session.rollback()
        code = -1
        msg = "删除失败"
    return response_tem(code=code, msg=msg, userdata=userdata)

#
# import jwt
#
# @task.route("/token", methods=["POST"])
# def get_token():
#     json_data = return_json(request)
#     tokon = json_data.get("tokon")
#     tokon = tokon.encode()
#     token = jwt.decode(tokon, "40EDE6AD-C07B-4760-F68D-08D56C70ED44",audience="新系统1", algorithms=['HS256'])
#     return json.dumps(token)

@task.route("/ttnginx")
def ttnginx():
    return 'nginx is ok hello,changhao'
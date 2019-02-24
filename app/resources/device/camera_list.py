import json
from flask import Blueprint, jsonify
from flask import request, make_response
from sqlalchemy import and_
from loggings import logger
from . import device
from app.models.models import Camera
from app import db


def get_json(request):
    json_str = str(request.get_data(), encoding='utf-8')
    task_info = json.loads(json_str)
    return task_info


def get_res(num, userdata):
    ret = dict()
    ret["code"] = num
    ret["userdata"] = userdata
    logger.debug("返回的json是：{}".format(ret))
    return jsonify(ret)


# 2.摄像机
# 2.1查询分组下摄像机列表
# URL: https://ip:port/api/v1/groups/searchCameraByGroup
@device.route("/searchCameraByGroup", methods=["GET"])
def search_camera_list():
    logger.info("收到查询分组下摄像机列表命令")
    data_list = list()
    ret = dict()
    try:
        task_info = get_json(request)
        logger.info("收到的json是:{}".format(str(task_info)))
        group_id = task_info["group_id"]
        userdata = task_info["userdata"]
        logger.info((group_id, userdata))
    except BaseException as e:
        # json格式错误
        logger.error(e)
        return get_res(-1, userdata)
    # 对camera表进行查询
    try:
        camerainfo_list = Camera.query.filter(
            and_(Camera.cameragroup_id == group_id, Camera.is_delete == False)).all()
        for camerainfo in camerainfo_list:
            camera_dict = dict()
            camera_dict["camera_id"] = camerainfo.id
            camera_dict["camera_name"] = camerainfo.camera_name
            data_list.append(camera_dict)
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        return get_res(-1, userdata)
    ret["code"] = 0
    ret["data"] = data_list
    ret["userdata"] = userdata
    logger.debug("返回的json是：{}".format(ret))
    return jsonify(ret)


# 2.2分组下添加摄像机
# URL: https://ip:port/api/v1/groups/addCameraByGroup
# Method: PUT
@device.route("/addCameraByGroup", methods=["PUT"])
def add_camera_list():
    logger.info("收到分组下添加摄像机命令")
    try:
        task_info = get_json(request)
        logger.info("收到的json是:{}".format(str(task_info)))
        group_id = task_info["group_id"]
        camera_list = task_info["camera_list"]
        userdata = task_info["userdata"]
        logger.info((group_id, camera_list, userdata))
    except BaseException as e:
        # json格式错误
        logger.error(e)
        return get_res(-1, userdata)

    try:
        for camera_id in camera_list:
            camerainfo = Camera.query.filter(
                and_(Camera.id == camera_id, Camera.is_delete == False)).first()
            camerainfo.cameragroup_id = group_id
            db.session.add(camerainfo)
        db.session.commit()
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        db.session.rollback()
        return get_res(-1, userdata)
    logger.info("分组下添加摄像机成功")
    return get_res(0, userdata)


# 2.3分组下删除摄像机
# URL: https://ip:port/api/v1/groups/deleteCameraByGroup
# Method: PUT
@device.route("/deleteCameraByGroup", methods=["PUT"])
def delete_camera_list():
    logger.info("收到分组下删除摄像机命令")
    try:
        task_info = get_json(request)
        logger.info("收到的json是:{}".format(str(task_info)))
        group_id = task_info["group_id"]
        camera_list = task_info["camera_list"]
        userdata = task_info["userdata"]
        logger.info((group_id, camera_list, userdata))
    except BaseException as e:
        # json格式错误
        logger.error(e)
        return get_res(-1, userdata)

    try:
        for camera_id in camera_list:
            camerainfo = Camera.query.filter(
                and_(Camera.id == camera_id, Camera.is_delete == False)).first()
            camerainfo.cameragroup_id = None
            db.session.add(camerainfo)
        db.session.commit()
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        db.session.rollback()
        return get_res(-1, userdata)
    logger.info("分组下删除摄像机成功")
    return get_res(0, userdata)


# 2.4摄像头名称模糊查询
# URL: https://ip:port/api/v1/groups/dimSearchCamera
# Method: GET
@device.route("/dimSearchCamera", methods=["GET"])
def dimsearch_camera_list():
    logger.info("摄像头名称模糊查询命令")
    data_list = list()
    ret = dict()
    try:
        task_info = get_json(request)
        logger.info("收到的json是:{}".format(str(task_info)))
        pagesize = task_info["pagesize"]
        pagenum = task_info["pagenum"]
        keyword = task_info["keyword"]
        userdata = task_info["userdata"]
        logger.info((pagesize, pagenum, keyword, userdata))
    except BaseException as e:
        # json格式错误
        logger.error(e)
        return get_res(-1, userdata)
    try:
        if keyword:
            # 对camera表进行查询
            pagination = Camera.query.filter(
                and_(Camera.camera_name.like("%" + keyword + "%"),
                     Camera.cameragroup_id == None,Camera.is_delete == False)).paginate(
                pagenum, per_page=pagesize, error_out=False)
        else:
            pagination = Camera.query.filter(
                and_(Camera.cameragroup_id == None, Camera.is_delete == False)).paginate(
                pagenum, per_page=pagesize, error_out=False)
        camerainfo_list = pagination.items
        for camerainfo in camerainfo_list:
            camera_dict = dict()
            camera_dict["camera_id"] = camerainfo.id
            camera_dict["camera_name"] = camerainfo.camera_name
            data_list.append(camera_dict)
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        return get_res(-1, userdata)
    ret["code"] = 0
    ret["data"] = data_list
    ret["all_page"] = pagination.pages
    ret["page"] = pagination.page
    ret["all_data"] = pagination.total
    ret["userdata"] = userdata
    logger.debug("返回的json是：{}".format(ret))
    return jsonify(ret)

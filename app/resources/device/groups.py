
import json
from flask import Blueprint, jsonify
from flask import request
from sqlalchemy import and_
from loggings import logger
from . import device
from app.models.models import CameraGroup
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


# 1.分组管理
# 1.1添加摄像机分组
# URL: https://ip:port/api/v1/groups/addGroup
@device.route("/addGroup", methods=["POST"])
def add_camera_groups():
    logger.info("收到添加摄像机分组命令")
    try:
        task_info = get_json(request)
        logger.info("收到的json是:{}".format(str(task_info)))
        group_name = task_info["group_name"]
        group_desc = task_info["group_desc"]
        parent_id = task_info["parent_id"]
        userdata = task_info["userdata"]
        logger.info((group_name, group_desc, parent_id, userdata))
    except BaseException as e:
        # json格式错误
        logger.error(e)
        return get_res(-1, userdata)

    try:
        check_name = CameraGroup.query.filter(
            and_(CameraGroup.group_name == group_name, CameraGroup.is_delete == False)).first()
        if check_name:
            logger.error("摄像机分组名称:{}已存在".format(group_name))
            return get_res(-1, userdata)
        if parent_id:
            check_parent_id = CameraGroup.query.filter(
                and_(CameraGroup.id == parent_id, CameraGroup.is_delete == False)).first()
            if check_parent_id is None:
                logger.error("摄像机分组id不存在:{}".format(parent_id))
                return get_res(-1, userdata)

        # 添加摄像机分组
        camera_group = CameraGroup()
        # camera_group.id = str(uuid.uuid4())
        camera_group.group_name = group_name
        camera_group.group_desc = group_desc
        camera_group.parent_id = parent_id
        logger.debug(camera_group)
        camera_group.add()
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        camera_group.rollback()
        return get_res(-1, userdata)
    logger.info("添加摄像机分组成功")
    return get_res(0, userdata)


# 1.2删除摄像机分组
# URL: https://ip:port/api/v1/groups/deleteGroup
@device.route("/deleteGroup", methods=["PUT"])
def delete_camera_groups():
    logger.info("收到删除摄像机分组命令")
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

    # 对group_id进行查询
    try:
        groupinfo = CameraGroup.query.filter(
            and_(CameraGroup.id == group_id, CameraGroup.is_delete == False)).first()
        if groupinfo is None:
            logger.error("摄像头分组id不存在")
            return get_res(-1, userdata)
        group_list = CameraGroup.query.filter(
            and_(CameraGroup.parent_id == group_id, CameraGroup.is_delete == False)).all()
        if len(group_list) is not 0:
            logger.error("该摄像机分组下摄像机不为空")
            for group in group_list:
                group.parent_id = None
                db.session.add(group)
        groupinfo.is_delete = True
        db.session.add(groupinfo)
        db.session.commit()
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        db.session.rollback()
        return get_res(-1, userdata)

    logger.info("删除摄像机分组成功")
    return get_res(0, userdata)


# 1.3编辑摄像机分组
# URL: https://ip:port/api/v1/groups/updateGroup
@device.route("/updateGroup", methods=["PUT"])
def update_camera_groups():
    logger.info("收到编辑摄像机分组命令")
    try:
        task_info = get_json(request)
        logger.info("收到的json是:{}".format(str(task_info)))
        group_id = task_info["group_id"]
        group_name = task_info["group_name"]
        group_desc = task_info["group_desc"]
        parent_id = task_info["parent_id"]
        userdata = task_info["userdata"]
        logger.info((group_id, group_name, group_desc, parent_id, userdata))
    except BaseException as e:
        # json格式错误
        logger.error(e)
        return get_res(-1, userdata)

    # 对group_id进行查询
    try:
        groupinfo = CameraGroup.query.filter(
            and_(CameraGroup.id == group_id, CameraGroup.is_delete == False)).first()
        if groupinfo is None:
            logger.error("摄像头分组id不存在")
            return get_res(-1, userdata)
        if parent_id:
            check_parent_id = CameraGroup.query.filter(
                and_(CameraGroup.id == parent_id, CameraGroup.is_delete == False)).first()
            if check_parent_id is None:
                logger.error("摄像机分组id不存在:{}".format(parent_id))
                return get_res(-1, userdata)
        groupinfo.group_name = group_name
        groupinfo.group_desc = group_desc
        groupinfo.parent_id = parent_id
        groupinfo.update()
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        groupinfo.rollback()
        return get_res(-1, userdata)

    logger.info("编辑摄像机分组成功")
    return get_res(0, userdata)


# 1.4查询摄像机分组树
# URL: https://ip:port/api/v1/groups/searchGroup
@device.route("/searchGroup", methods=["GET"])
def search_camera_groups():
    logger.info("收到查询摄像机分组树命令")
    try:
        task_info = get_json(request)
        logger.info("收到的json是:{}".format(str(task_info)))
        userdata = task_info["userdata"]
        logger.info(userdata)
    except BaseException as e:
        # json格式错误
        logger.error(e)
        return get_res(-1, userdata)
    data_list = list()
    ret = dict()
    # 对camera_group表进行查询
    try:
        groupinfo_list = CameraGroup.query.filter(CameraGroup.is_delete == False).all()
        for groupinfo in groupinfo_list:
            group_dict = dict()
            group_dict["group_id"] = groupinfo.id
            group_dict["group_name"] = groupinfo.group_name
            group_dict["parent_id"] = groupinfo.parent_id
            data_list.append(group_dict)
    except BaseException as e:
        # 接口调用失败
        logger.error(e)
        return get_res(-1, userdata)
    ret["code"] = 0
    ret["data"] = data_list
    ret["userdata"] = userdata
    logger.debug("返回的json是：{}".format(ret))
    return jsonify(ret)
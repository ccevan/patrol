#! python3
# date: 2018/7/3

import logging
import uuid, json
from app import db
from app.resources.device import device
from flask import request, jsonify
from app.models.models import Camera, Organization, CameraProtocol, Channel
from app.forms.cameraform import CameraForm
from sqlalchemy.orm.interfaces import PropComparator, operators
from sqlalchemy import DateTime, and_, or_, asc, desc

logger = logging.getLogger('patrol.camera')


@device.route('/addCamera', methods=['POST'])
def add_camera():
    """添加摄像头"""
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    form = CameraForm.from_json(request.json)
    userdata = request.json.get('userdata')
    if request.method == 'POST' and form.validate():
        args = form.data
        args['cameragroup_id'] = args['cameragroup_id'] or None  # 不能为空字符串
        args['cameraprotocol_id'] = args['cameraprotocol_id'] or None  # 不能为空字符串
        args['organization_id'] = args['organization_id'] or None  # 不能为空字符串
        args['cameratype_id'] = args['cameratype_id'] or None  # 不能为空字符串

        camera = Camera(**args)
        try:
            db.session.add(camera)
            db.session.commit()
        except Exception as e:  # SQLAlchemy 其他错误
            logger.error('database error:{}'.format(e))
            return render_response(code=-1, msg="database error.",
                                   userdata=userdata)

        return render_response(code=0, msg="add camera success.",
                               userdata=userdata)
    else:
        logger.error("parameter validate error:{}".format(form.errors))
        msg = "parameter validate error:{}".format(form.errors)
        return render_response(code=-1, msg=msg, userdata=userdata)


@device.route('/deleteCameraById', methods=['POST'])
def delete_camera_by_id():
    """通过相机ID 删除相机"""
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    camera_ids = request.json.get('camera_id')
    userdata = request.json.get('userdata')
    is_delete = request.json.get('is_delete', True)
    if isinstance(camera_ids, str):
        camera_ids = [camera_ids]

    for camera_id in camera_ids:
        camera = Camera.query.get(camera_id)
        if camera is None:  # 相机id不存在
            msg = "camera_id:{} not exist.".format(camera_id)
            return render_response(code=-1,
                                   msg=msg,
                                   userdata=userdata)
        # 删除摄像头
        camera.is_delete = is_delete
        db.session.add(camera)
        # 删除摄像头下的通道
        for channel in camera.channels:
            channel.is_delete = True
            db.session.add(channel)
    try:
        db.session.commit()
    except Exception as e:
        logger.debug('database error:{}'.format(e))
        return render_response(code=-1,
                               msg="database error.",
                               userdata=userdata)

    return render_response(code=0,
                           msg='delete camera success',
                           userdata=userdata)


@device.route('/updateCamera', methods=['POST'])
def update_camera():
    """更新摄像机信息"""
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    form = CameraForm.from_json(request.json)

    userdata = request.json.get('userdata')
    camera_id = request.json.get("camera_id")
    if request.method == 'POST' and form.validate():
        if not camera_id:
            logger.error('camera id required.')
            return render_response(code=-1,
                                   msg='camera id required.',
                                   userdata=userdata)
        # 根据id获取相机
        camera = Camera.query.get(camera_id)
        if camera is None:
            logger.error('camera id not exist.')
            return render_response(code=-1,
                                   msg='camera id not exist.',
                                   userdata=userdata)
        # 修改摄像机属性
        camera.camera_name = form.camera_name.data
        camera.camera_manufacturer = form.camera_manufacturer.data
        camera.camera_channel = form.camera_channel.data
        camera.camera_ip = form.camera_ip.data
        camera.camera_port = form.camera_port.data
        camera.camera_account = form.camera_account.data
        camera.camera_password = form.camera_password.data
        camera.camera_desc = form.camera_desc.data
        camera.cameragroup_id = form.cameragroup_id.data or None
        camera.cameraprotocol_id = form.cameraprotocol_id.data or None

        camera.heartbeat_timeout_secs = form.heartbeat_timeout_secs.data
        camera.heartbeat_timeout_times = form.heartbeat_timeout_times.data
        camera.registration_period = form.registration_period.data
        camera.cameratype_id = form.cameratype_id.data or None
        camera.organization_id = form.organization_id.data or None
        camera.cameraplatform_id = form.cameraplatform_id.data or None
        try:
            db.session.add(camera)
            db.session.commit()
        except Exception as e:  # SQLAlchemy 其他错误
            logger.error("database error:{}".format(e))
            return render_response(code=-1, msg="database error.",
                                   userdata=userdata)

        return render_response(code=0, userdata=userdata)
    else:
        logger.error("parameter validate error:{}".format(form.errors))
        return render_response(code=-1,
                               msg="parameter validate error:{}".format(form.errors),
                               userdata=userdata)


@device.route('/getCameraById', methods=['POST'])
def get_camera_by_id():
    """根据 id 获取相机信息"""
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    camera_id = request.json.get('camera_id')
    userdata = request.json.get('userdata')

    if not is_uuid(camera_id):
        logger.error('camera_id is not uuid.')
        return render_response(code=-1,
                               msg='camera_id is not uuid.',
                               userdata=userdata)

    camera = db.session.query(Camera). \
        filter_by(id=camera_id, is_delete=False).first()
    # 没有找到摄像机
    if camera is None:
        return render_response(code=-1,
                               msg='camera not exist',
                               userdata=userdata)
    data = camera.to_json()

    return render_response(code=0, data=data, userdata=userdata)


@device.route('/searchCamera', methods=['POST'])
def search_camera():
    # 根据相机名称或ip搜索摄像机
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    json = request.json
    page = int(json.get('page', 1) or 1)
    page_size = int(json.get('page_size', 20) or 20)
    userdata = json.get('userdata')
    name = json.get('camera_name')
    ip = json.get('camera_ip')
    port = json.get('camera_port')
    camera_status = json.get('camera_status')
    cameratype_id = json.get('cameratype_id')
    protocol_id = json.get('cameraprotocol_id')
    organization = json.get('organization_id')
    start_date = json.get('start_date')
    end_date = json.get('end_date')
    sort_field = json.get('sort_field', 'update_time') or "create_time"
    sort_order = json.get('sort_order', 'desc') or "desc"

    cam_kwargs = dict()
    # 精准查找

    try:
        port = int(port)
        cam_kwargs["camera_port"] = port
    except:
        pass
    try:
        camera_status = int(camera_status)
        cam_kwargs["camera_status"] = camera_status
    except:
        pass

    if ip:
        cam_kwargs["camera_ip"] = ip
    if cameratype_id:
        cam_kwargs['cameratype_id'] = cameratype_id
    if protocol_id:
        cam_kwargs['cameraprotocol_id'] = protocol_id

    cameras = Camera.query.filter_by(is_delete=False, **cam_kwargs)

    # 模糊查找
    filter_params = []
    if start_date:
        filter_params.append(Camera.update_time >= start_date)
    if end_date:
        filter_params.append(Camera.update_time <= end_date)
    if organization:
        try:
            organization_id = uuid.UUID(organization).hex
            filter_params.append(Camera.organization_id == organization_id)
        except:
            org_ids = db.session.query(Organization.id).filter(
                Organization.organization_name.like('%' + organization + '%'))
            filter_params.append(Camera.organization_id.in_(org_ids))
    if name:
        filter_params.append(Camera.camera_name.like('%' + name + '%'))

    # 排序的顺序
    if sort_order == "asc":
        sort_order = asc
    else:
        sort_order = desc

    # 排序的字段
    if sort_field == "create_time":
        sort_field = Camera.create_time
    elif sort_field == "update_time":
        sort_field = Camera.update_time

    cameras = cameras.filter(and_(*filter_params)).order_by(sort_order(sort_field))
    pagination = cameras.paginate(page, per_page=page_size, error_out=False)

    data = []
    for each in pagination.items:
        data.append(each.to_json())

    return render_response(code=0, data=data,
                           page=pagination.page,
                           all_page=pagination.pages,
                           all_data=pagination.total,
                           userdata=userdata)


# @device.route('/getCameraByGroupId', methods=['POST'])
# def get_camera_by_group_id():
#     """根据分组ID获取相机列表"""
#
#     group_id = request.json.get('group_id')
#     userdata = request.json.get('userdata')
#
#     if not is_uuid(group_id):
#         logger.error('group_id must be uuid.')
#         return render_response(code=-1,
#                                msg='group_id must be uuid.',
#                                userdata=userdata)
#
#     camera_objs = CameraGroup.query.get(group_id).cameras
#
#     data = []
#     for each in camera_objs:
#         data.append(each.to_json())
#
#     return render_response(code=0, data=data, userdata=userdata)


def render_response(code, data=None, msg=None,
                    page=None, all_page=None,
                    all_data=None, userdata=None):
    res = {
        'code': code,
        'data': data,
        'msg': msg,
        "userdata": userdata
    }
    if page:
        res['page'] = page
    if all_page:
        res['all_page'] = all_page
    if all_data:
        res['all_data'] = all_data
    return jsonify(res)


def is_uuid(value):
    try:
        uuid.UUID(value)
    except Exception:
        return False
    return True
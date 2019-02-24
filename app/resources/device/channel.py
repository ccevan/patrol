#! python3
# __author__ = "YangJiaHao"
# date: 2018/9/7
import uuid
from app.resources.device import device
from flask import request, jsonify
from app.models.models import Channel, Camera
from app.forms.cameraform import ChannelForm
from app import db
from loggings import logger


@device.route("/addChannel", methods=["POST"])
def add_channel():
    """添加通道"""
    if not request.content_type == 'application/json':
        return render_response(-1,msg="Content-type must be application/json.")

    form = ChannelForm.from_json(request.json)
    if not form.validate():
        msg = "Content-type error:{}".format(form.errors)
        logger.warning(msg)
        return render_response(-1, msg=msg)
    try:
        kwargs = form.data
        channel = Channel(**kwargs)
        channel.add()
    except Exception as e:
        logger.error(e)
        return render_response(-1, msg='database error')
    return render_response(0)


@device.route("/deleteChannel", methods=["POST"])
def delete_channel():
    """删除通道，支持单个和批量删除"""
    if not request.content_type == 'application/json':
        return render_response(-1,msg="Content-type must be application/json.")

    ids = request.json.get('channel_id')
    if isinstance(ids, str):
        ids = [ids]
    try:
        for id in ids:
            channel = Channel.query.get(id)
            if channel is None:
                msg = 'channel id :{} not exist'.format(id)
                render_response(-1, msg=msg)
            channel.is_delete = True
            db.session.add(channel)
        db.session.commit()
    except Exception as e:
        logger.error(e)
        return render_response(-1, msg='data base error')
    return render_response(0)


@device.route("/searchChannel", methods=["POST"])
def search_channel():
    """搜索通道，支持多条件过滤，排序功能"""
    if not request.content_type == 'application/json':
        return render_response(-1,msg="Content-type must be application/json.")

    page = request.json.get('page', 1)
    page_size = request.json.get('page_size', 20)

    channel_name = request.json.get('channel_name')
    camera_name = request.json.get('camera_name')
    org_id = request.json.get('organization_id')
    platform_id = request.json.get('platform_id')
    camera_id = request.json.get("camera_id")
    yun_tai =  request.json.get("yun_tai")
    status = request.json.get("status")
    userdata = request.json.get('userdata')
    sort_field = request.json.get('sort_field', 'create_time') or "create_time"
    sort_order = request.json.get('sort_order', 'desc') or "desc"

    filter_params = []
    if camera_name:
        filter_params.append(Camera.camera_name.like("%" + camera_name + "%"))
    if org_id:
        filter_params.append(Camera.organization_id == org_id)
    if platform_id:
        filter_params.append(Camera.cameraplatform_id == platform_id)
    if channel_name:
        filter_params.append(Channel.channel_name.like("%" + channel_name + "%"))

    if camera_id:
        filter_params.append(Channel.camera_id == camera_id)
    if type(yun_tai) is int:
        filter_params.append(Channel.yun_tai == yun_tai)
    if type(status) is int:
        filter_params.append(Channel.status == status)


    try:
        sort_field = getattr(Channel, sort_field)
        sort_params = getattr(sort_field, sort_order)()
    except:
        sort_params = getattr(Channel.create_time, sort_order)()

    pagination = db.session.query(Channel, Camera). \
        filter(Channel.is_delete == False, Channel.camera_id == Camera.id). \
        filter(*filter_params).order_by(sort_params). \
        paginate(page, per_page=page_size, error_out=False)

    data = []
    for channel, camera in pagination.items:
        col = dict()
        col["channel_id"] = channel.id
        col["channel_name"] = channel.channel_name
        col["channel_number"] = channel.channel_number
        col["camera_id"] = camera.id
        col["camera_name"] = camera.camera_name
        col["organization_id"] = camera.organization_id
        col["platform_id"] = camera.cameraplatform_id
        col["gb_number"] = channel.gb_number
        col["yun_tai"] = channel.yun_tai
        col["status"] = channel.status
        col["creator"]= 'admin'
        col["create_time"] = channel.create_time.strftime("%Y-%m-%d %H:%M:%S")
        col["update_time"] = channel.update_time.strftime("%Y-%m-%d %H:%M:%S")
        col["platform_name"] = camera.cameraplatform.camera_platform_name \
            if camera.cameraplatform_id else ''
        col["organization_name"] = camera.organization.organization_name \
            if camera.organization_id else ''

        data.append(col)

    return render_response(code=0, data=data,
                           page=pagination.page,
                           all_page=pagination.pages,
                           all_data=pagination.total,
                           userdata=userdata)


@device.route("/getChannelById", methods=["POST"])
def get_channel_by_id():
    """通过id获取通道"""
    if not request.content_type == 'application/json':
        return render_response(-1,msg="Content-type must be application/json.")

    channel_id = request.json.get('channel_id')

    rep = db.session.query(Channel, Camera). \
        filter(Channel.is_delete == False, Channel.id == channel_id).first()
    if not rep:
        logger.warning("channel not exist. id:{}".format(channel_id))
        return render_response(-1, msg="channel not exist")
    else:
        channel, camera = rep
        data = dict()
        data["channel_id"] = channel.id
        data["channel_name"] = channel.channel_name
        data["channel_number"] = channel.channel_number
        data["camera_id"] = channel.camera.id
        data["camera_name"] = channel.camera.camera_name
        data["organization_id"] = channel.camera.organization_id
        data["platform_id"] = channel.camera.cameraplatform_id
        data["gb_number"] = channel.gb_number
        data["yun_tai"] = channel.yun_tai
        data["status"] = channel.status
        data["creator"] = "admin"
        data["create_time"] = channel.create_time.strftime("%Y-%m-%d %H:%M:%S")
        data["update_time"] = channel.update_time.strftime("%Y-%m-%d %H:%M:%S")
        data["organization_name"] = camera.organization.organization_name \
            if camera.organization_id else ""
        data["platform_name"] = camera.cameraplatform.camera_platform_name \
            if camera.cameraplatform_id else ""

    return render_response(0, data=data)


@device.route("/updateChannel", methods=["POST"])
def update_channel():
    """更新通道"""
    if not request.content_type == 'application/json':
        return render_response(-1,msg="Content-type must be application/json.")

    form = ChannelForm.from_json(request.json)
    channel_id = request.json.get('channel_id')

    if not form.validate() or not is_uuid(channel_id):
        msg = "parameter error:{}".format(form.errors)
        logger.warning(msg)
        return render_response(-1, msg=msg)

    channel = Channel.query.get(channel_id)
    if not channel:
        msg = "channel_id: {} is not exist".format(channel_id)
        logger.error(msg)
        return render_response(-1, msg=msg)

    channel.camera_id = form.camera_id.data
    channel.channel_name = form.channel_name.data
    channel.channel_number = form.channel_number.data
    channel.gb_number = form.gb_number.data
    channel.yun_tai = form.yun_tai.data
    channel.status = form.status.data
    try:
        channel.update()
    except Exception as e:
        logger.error()
        return render_response(-1, msg='datebase error')
    return render_response(0)


def is_uuid(id):
    try:
        uuid.UUID(id)
        return True
    except:
        return False


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
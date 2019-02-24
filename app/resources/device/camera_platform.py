
from app.resources.device import device
from flask import request
from app.models.models import CameraGroup, Camera, CameraPlatform, CameraProtocol, CameraPlatformType, Organization, CameraType
from app import db
import json
from config import BaseConfig
from loggings import logger
from sqlalchemy import and_


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


@device.route("/addPlatform",  methods=["POST"])
def add_platform():
    """
    Add video platform information
    添加视频平台信息
    :return:
    """

    json_data = return_json(request)
    platformtype_id = json_data.get("platformtype_id",  None)
    organization_id = json_data.get("organization_id",  None)
    camera_platform_name = json_data.get("camera_platform_name",  None)
    camera_platform_ip = json_data.get("camera_platform_ip",  None)
    camera_platform_port = json_data.get("camera_platform_port",  None)
    camera_platform_account = json_data.get("camera_platform_account",  None)
    camera_platform_password = json_data.get("camera_platform_password",  None)
    camera_platform_status = json_data.get("camera_platform_status",  None)
    gb_number = json_data.get("gb_number", None)
    registration_period = json_data.get("registration_period", None)
    heartbeat_timeout_secs = json_data.get("heartbeat_timeout_secs", None)
    heartbeat_timeout_times = json_data.get("heartbeat_timeout_times", None)
    # create_user_id = json_data.get("create_user_id", None)
    user_data = json_data.get("userdata",  None)

    status = BaseConfig.PLATFORM_STATUS

    if not (camera_platform_ip and camera_platform_ip and camera_platform_name and platformtype_id and organization_id and camera_platform_status):
        code = -1
        msg = "添加平台必须有平台名称,平台类型,所属组织机构,ip地址,端口,平台状态"
        return response_tem(code=code, msg=msg, userdata=user_data)
    if not len(platformtype_id) == 32:
        code = -1
        msg = "平台外键长度应该是32位"
        return response_tem(code=code, msg=msg, userdata=user_data)
    if not len(organization_id) == 32:
        code = -1
        msg = "组织机构外键长度应该是32位"
        return response_tem(code=code, msg=msg, userdata=user_data)

    # if not len(organization_id) == 36:
    #     code = -1
    #     msg = "组织机构外键长度应该是36位"
    #     return response_tem(code=code, msg=msg, userdata=user_data)

    if type(camera_platform_port) is str and not camera_platform_port.isdigit():
        code = -1
        msg = "端口号必须是数字类型"
        return response_tem(code=code, msg=msg, userdata=user_data)
    if type(camera_platform_status) is str and not camera_platform_status.isdigit():
        code = -1
        msg = "状态必须是数字类型 1-在线, 0-离线"
        return response_tem(code=code, msg=msg, userdata=user_data)
    camera_platform_port = int(camera_platform_port)
    camera_platform_status = int(camera_platform_status)

    if camera_platform_status not in status:
        code = -1
        msg = "状态码： 1-在线, 0-离线"
        return response_tem(code=code, msg=msg, userdata=user_data)

    try:
        platform_type = CameraPlatformType.query.filter_by(id=platformtype_id).first()
        #Todo 组织机构的验证需要去掉
        organization = Organization.query.filter_by(id=organization_id).first()
        if not organization:
            code = -1
            msg = "该组织机构不存在"
            return response_tem(code=code, msg=msg, userdata=user_data)
        if not platform_type:
            code = -1
            msg = "该平台类型不存在"
            return response_tem(code=code, msg=msg, userdata=user_data)
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "校验组织机构或者平台类型时出错"
        return response_tem(code=code, msg=msg, userdata=user_data)

    try:

        param = {
            "camera_platform_name": camera_platform_name,
            "camera_platform_ip": camera_platform_ip,
            "camera_platform_port": camera_platform_port,
            "platformtype_id": platformtype_id,
            "organization_id": organization_id,
            "camera_platform_account": camera_platform_account,
            "camera_platform_status": camera_platform_status,
            "gb_number": gb_number,
            "registration_period": registration_period,
            "heartbeat_timeout_secs": heartbeat_timeout_secs,
            "heartbeat_timeout_times": heartbeat_timeout_times,
            "camera_platform_password": camera_platform_password,
            # "create_user_id": create_user_id if create_user_id else None
        }
        platform = CameraPlatform(**param)
        db.session.add(platform)
        db.session.commit()
        code = 0
        msg = "信息添加成功"
    except Exception as e: 
        db.session.rollback()
        logger.error(e)
        code = -1
        msg = "信息添加失败"
    return response_tem(code=code, msg=msg, userdata=user_data)


@device.route("/platformInfo",  methods=["POST"])
def get_platform_info_by_id():
    """
    Obtain platform information based on video platform id
    根据视频平台id获取平台信息
    :return:
    """
    json_data = return_json(request)
    p_id = json_data.get("id", None)
    user_data = json_data.get("userdata", None)
    if p_id is None:
        code = -1
        msg = "没有获取到需要查询的id"
        return response_tem(code=code, msg=msg, userdata=user_data)

    all_info = []

    try: 
        platform = CameraPlatform.query.filter_by(id=p_id, is_delete=False).first()
        #Todo 组织机构的返回字段只需要id
        platform_info = {
            "cameraplatform_id": platform.id,
            "camera_platform_name": platform.camera_platform_name,
            "camera_platform_channel": platform.camera_platform_channel,
            "camera_platform_ip": platform.camera_platform_ip,
            "camera_platform_port": platform.camera_platform_port,
            "camera_platform_account": platform.camera_platform_account,
            "camera_platform_password": platform.camera_platform_password,
            "camera_platform_desc": platform.camera_platform_desc,
            "camera_platform_status": platform.camera_platform_status,
            "organization_name": platform.organization.organization_name if platform.organization_id else None,
            "organization_id": platform.organization.id if platform.organization_id else None,
            "camera_platform_type": platform.platformtype.camera_platform_type if platform.platformtype_id is not None else None,
            "platformtype_id": platform.platformtype.id if platform.platformtype_id is not None else None,
            # "create_user_id": platform.create_user_id,
            # "update_user_id": platform.update_user_id,
            "create_time": platform.create_time,
            "update_time": platform.update_time
        }

        if platform.gb_number is not None:
            platform_info["gb_number"] = platform.gb_number
            platform_info["registration_period"] = platform.registration_period
            platform_info["heartbeat_timeout_secs"] = platform.heartbeat_timeout_secs
            platform_info["heartbeat_timeout_times"] = platform.heartbeat_timeout_times

        all_info.append(platform_info)
        code = 0
        msg = "查询成功"

    except Exception as e: 
        code = -1
        msg = "查询失败"
        logger.error(e)

    return response_tem(code=code, data=all_info, msg=msg, userdata=user_data)


@device.route("/modifyPlatform",  methods=["POST"])
def modify_form():
    """
    Modify platform information based on id
    根据平台id获取平台信息, 修改数据后, post请求提交, 入库
    :return:
    """
    json_data = return_json(request)
    p_id = json_data.get("cameraplatform_id", None)
    platformtype_id = json_data.get("platformtype_id", None)
    organization_id = json_data.get("organization_id", None)
    camera_platform_name = json_data.get("camera_platform_name", None)
    camera_platform_ip = json_data.get("camera_platform_ip", None)
    camera_platform_port = json_data.get("camera_platform_port", None)
    camera_platform_status = json_data.get("camera_platform_status", None)
    camera_platform_account = json_data.get("camera_platform_account", None)
    camera_platform_password = json_data.get("camera_platform_password", None)
    gb_number = json_data.get("gb_number", None)
    registration_period = json_data.get("registration_period", None)
    heartbeat_timeout_secs = json_data.get("heartbeat_timeout_secs", None)
    heartbeat_timeout_times = json_data.get("heartbeat_timeout_times", None)
    # update_user_id = json_data.get("update_user_id", None)
    userdata = json_data.get("userdata", None)

    status = BaseConfig.PLATFORM_STATUS

    if not (camera_platform_ip and camera_platform_ip
            and camera_platform_name and platformtype_id
            and organization_id and camera_platform_status):
        code = -1
        msg = "添加平台必须有平台名称,平台类型,所属组织机构,ip地址,端口,平台状态"
        return response_tem(code=code, msg=msg, userdata=userdata)
    if not len(platformtype_id) == 32:
        code = -1
        msg = "平台外键长度应该是32位"
        return response_tem(code=code, msg=msg, userdata=userdata)
    if not len(organization_id) == 32:
        code = -1
        msg = "组织机构外键长度应该是32位"
        return response_tem(code=code, msg=msg, userdata=userdata)

    # if not len(organization_id) == 36:
    #     code = -1
    #     msg = "组织机构外键长度应该是36位"
    #     return response_tem(code=code, msg=msg, userdata=userdata)

    if type(camera_platform_port) is str and not camera_platform_port.isdigit():
        code = -1
        msg = "端口号必须是数字类型"
        return response_tem(code=code, msg=msg, userdata=userdata)
    if type(camera_platform_status) is str and not camera_platform_status.isdigit():
        code = -1
        msg = "状态必须是数字类型 1-在线, 0-离线"
        return response_tem(code=code, msg=msg, userdata=userdata)
    camera_platform_port = int(camera_platform_port)
    camera_platform_status = int(camera_platform_status)

    if camera_platform_status not in status:
        code = -1
        msg = "状态码： 1-在线, 0-离线"
        return response_tem(code=code, msg=msg, userdata=userdata)
    try:
        platform_type = CameraPlatformType.query.filter_by(id=platformtype_id).first()
        organization = Organization.query.filter_by(id=organization_id).first()
        if not organization:
            code = -1
            msg = "该组织机构不存在"
            return response_tem(code=code, msg=msg, userdata=userdata)
        if not platform_type:
            code = -1
            msg = "该平台类型不存在"
            return response_tem(code=code, msg=msg, userdata=userdata)
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "校验组织机构或者平台类型时出错"
        return response_tem(code=code, msg=msg, userdata=userdata)

    try:
        #Todo 组织机构的验证去掉
        platform_type = CameraPlatformType.query.filter_by(id=platformtype_id).first()
        organization = Organization.query.filter_by(id=organization_id).first()
        platform = CameraPlatform.query.filter_by(id=p_id, is_delete=False).first()

        if not organization:
            code = -1
            msg = "该组织机构不存在"
            return response_tem(code=code, msg=msg, userdata=userdata)

        if not platform_type:
            code = -1
            msg = "该平台类型不存在"
            return response_tem(code=code, msg=msg, userdata=userdata)

        if not platform:
            code = -1
            msg = "该平台不存在或者已被删除"
            return response_tem(code=code, msg=msg, userdata=userdata)

        platform.camera_platform_name = camera_platform_name
        platform.camera_platform_ip = camera_platform_ip
        platform.camera_platform_port = camera_platform_port
        platform.platformtype_id = platformtype_id
        platform.organization_id = organization_id
        platform.camera_platform_account = camera_platform_account
        platform.camera_platform_password = camera_platform_password
        platform.gb_number = gb_number
        platform.registration_period = registration_period
        platform.heartbeat_timeout_secs = heartbeat_timeout_secs
        platform.heartbeat_timeout_times = heartbeat_timeout_times
        # platform.update_user_id = update_user_id
        db.session.add(platform)
        db.session.commit()
        code = 0
        msg = "更新成功"
    except Exception as e: 
        db.session.rollback()
        logger.error(e)
        code = -1
        msg = "更新失败"
    return response_tem(code=code, msg=msg, userdata=userdata)


@device.route("/deletePlatform", methods=["POST"])
def delete_platform():
    """
    Delete platform information based on platform id
    根据平台id删除平台信息
    :return:
    """
    json_data = return_json(request)
    ids = json_data.get("ids", None)
    user_data = json_data.get("userdata", None)
    if (type(ids) is str and not len(ids) == 32) or \
            ids is None or len(ids) == 0:
        code = -1
        msg = "ids格式非法"
        return response_tem(code=code, msg=msg, userdata=user_data)
    if type(ids) is list:
        for _id in ids:
            if not len(_id) == 32:
                code = -1
                msg = "ids格式非法"
                return response_tem(code=code, msg=msg, userdata=user_data)
    if type(ids) is str and len(ids) == 32:
        ids = [ids]
    try:
        for _id in ids:

            platform = CameraPlatform.query.filter_by(id=_id, is_delete=False).first()
            if not platform:
                code = -1
                msg = "id:{}不存在或已被删除".format(_id)
                logger.error(msg)
                return response_tem(code=code, msg=msg, userdata=user_data)
            for camera in platform.cameras.all():
                camera.is_delete = True
                db.session.add(camera)
            platform.is_delete = True
            db.session.add(platform)
        db.session.commit()

        code = 0
        msg = "删除平台信息成功"
    except Exception as e: 
        db.session.rollback()

        code = -1
        msg = "删除平台信息失败"
        logger.error(e)
    return response_tem(code=code, msg=msg, userdata=user_data)


@device.route("/cameraPlatform", methods=["POST"])
def search_platform_list():
    """
    模糊查询平台信息
    :return:
    """
    json_data = return_json(request)
    keywords = json_data.get("searchInfo", None)
    page = json_data.get("page", 1)

    page_size = json_data.get("page_size", 20)
    user_data = json_data.get("userdata", None)

    is_create = True
    is_desc = True

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
            platform_name = keywords.get("camera_platform_name", None)
            platform_addr = keywords.get("camera_platform_ip", None)
            platform_port = keywords.get("camera_platform_port", None)
            platform_type_id = keywords.get("platformtype_id", None)
            organization_id = keywords.get("organization_id", None)
            is_create = keywords.get("is_create", True)
            is_desc = keywords.get("is_desc", True)

            if organization_id and (not len(organization_id) == 32):
                code = -1
                msg = "所属组织机构的id长度为32"
                return response_tem(
                    code=code,
                    msg=msg,
                    userdata=user_data
                )
            if platform_type_id and (not len(platform_type_id) == 32):
                code = -1
                msg = "平台类型的id长度为32"
                return response_tem(
                    code=code,
                    msg=msg,
                    userdata=user_data
                )

            search_param = {
                "is_delete": False,
            }
            if organization_id:
                search_param["organization_id"] = organization_id
            if platform_type_id:
                search_param["platformtype_id"] = platform_type_id
            platforms = CameraPlatform.query.filter_by(**search_param).filter(
                and_(CameraPlatform.camera_platform_name.like("%"+platform_name+"%") if platform_name is not None else "",
                    CameraPlatform.camera_platform_ip.like("%"+platform_addr+"%") if platform_addr is not None else "",
                    CameraPlatform.camera_platform_port.like("%"+platform_port+"%") if platform_port is not None else ""
                     ))
        else:
            platforms = CameraPlatform.query.filter(
                CameraPlatform.is_delete == False)

        if is_create:
            if is_desc:
                pagination = platforms.order_by(CameraPlatform.create_time.desc()).paginate(page, page_size, error_out=False)
            else:
                pagination = platforms.order_by(CameraPlatform.create_time.asc()).paginate(page, page_size, error_out=False)
        else:
            if is_desc:
                pagination = platforms.order_by(CameraPlatform.update_time.desc()).paginate(page, page_size, error_out=False)
            else:
                pagination = platforms.order_by(CameraPlatform.update_time.asc()).paginate(page, page_size, error_out=False)

        all_data = pagination.total
        all_page = pagination.pages
        now_page = pagination.page
        all_platform = pagination.items
        if all_platform:
            for platform in all_platform:
                platform_info = {
                    "camera_platform_type": platform.platformtype.camera_platform_type,
                    "cameraplatform_id": platform.id,
                    "camera_platform_name": platform.camera_platform_name,
                    "camera_platform_ip": platform.camera_platform_ip,
                    "camera_platform_port": platform.camera_platform_port,
                    "organization_name": platform.organization.organization_name,
                    # "create_user_id": platform.create_user_id,
                    # "update_user_id": platform.update_user_id,
                    "create_time": platform.create_time,
                    "update_time": platform.update_time
                }
                camera_list = Camera.query.filter_by(is_delete=False, cameraplatform=platform).all()
                camera_numbers = len(camera_list)
                platform_info["camera_numbers"] = camera_numbers
                all_info.append(platform_info)
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
        data=all_info,
        msg=msg,
        userdata=user_data,
        all_data=all_data,
        all_page=all_page,
        page=now_page
    )


@device.route("/platformTimeOrder", methods=["POST"])
def time_order_by():
    """
    Sort by time
    根据时间排序
    :return:
    """
    json_data = return_json(request)
    page = json_data.get("page", None)
    page_size = json_data.get("page_size", None)
    is_create = json_data.get("is_create", True)
    is_desc = json_data.get("is_desc", True)
    user_data = json_data.get("userdata", None)

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
        if is_create:
            if is_desc:
                all_platform = CameraPlatform.query.filter_by(is_delete=False). \
                    order_by(CameraPlatform.create_time.desc()).paginate(page, page_size, 0)
            else:
                all_platform = CameraPlatform.query.filter_by(is_delete=False). \
                    order_by(CameraPlatform.create_time.asc()).paginate(page, page_size, 0)
        else:
            if is_desc:
                all_platform = CameraPlatform.query.filter_by(is_delete=False). \
                    order_by(CameraPlatform.update_time.desc()).paginate(page, page_size, 0)
            else:
                all_platform = CameraPlatform.query.filter_by(is_delete=False). \
                    order_by(CameraPlatform.update_time.asc()).paginate(page, page_size, 0)

        all_data = all_platform.total
        all_page = all_platform.pages  # 总页数
        now_page = all_platform.page  # 当前页

        for platform in all_platform.items:
            platform_info = {
                "cameraplatform_id": platform.id,
                "camera_platform_type": platform.platformtype.camera_platform_type,
                "camera_platform_name": platform.camera_platform_name,
                "camera_platform_ip": platform.camera_platform_ip,
                "camera_platform_port": platform.camera_platform_port,
                "of_organization": platform.organization.organization_name if platform.organization_id else None,
                # "create_user_id": platform.create_user_id,
                # "update_user_id": platform.update_user_id,
                "create_time": platform.create_time,
                "update_time": platform.update_time
            }
            camera_list = Camera.query.filter_by(is_delete=False, cameraplatform=platform).all()
            camera_numbers = len(camera_list)
            platform_info["camera_numbers"] = camera_numbers
            all_info.append(platform_info)
        code = 0
        msg = "搜索成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "搜索失败"
        now_page = None
        all_data = None
        all_page = None

    return response_tem(
        code=code,
        msg=msg,
        data=all_info,
        page=now_page,
        all_page=all_page,
        all_data=all_data,
        userdata=user_data
    )


@device.route("/allCameraProtocol")
def get_all_platform_protocol():
    """
    Get protocol types for all cameras
    获取所有相机的协议
    :return:
    """
    all_info = []

    try:
        all_camera_protocol = CameraProtocol.query.all()
        all_data = len(all_camera_protocol)
        for protocol in all_camera_protocol:
            all_info.append(protocol.to_json())
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
        all_data = None

    return response_tem(
        code=code,
        data=all_info,
        msg=msg,
        all_data=all_data
    )


@device.route("/allPlatformType")
def get_platform_type():
    """
    查询所有平台的类型
    :return:
    """

    all_info = []
    try:
        all_type = CameraPlatformType.query.all()
        all_data = len(all_type)
        for TYPE in all_type:
            all_info.append(TYPE.to_json())
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
        all_data = None
    return response_tem(
        code=code,
        data=all_info,
        msg=msg,
        all_data=all_data
    )


@device.route("/allCameraType")
def get_all_camera_type():
    """
    Get all camera types
    获取所有相机的类型, get
    :return:
    """
    all_info = []
    try:
        camera_types = CameraType.query.all()
        all_data = len(camera_types)
        for TYPE in camera_types:
            all_info.append(TYPE.to_json())
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
        all_data = None
    return response_tem(
        code=code, msg=msg,
        data=all_info,
        all_data=all_data
    )

#  批量导入摄像机

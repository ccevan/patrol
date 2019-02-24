
from . import device
from flask import request
from app.models.models import Organization, CameraPlatform, Camera
import json
from app import db
from loggings import logger
import paginate


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


org_list = []


def get_son(parent_org):
    org_list.append(parent_org)
    for org in parent_org.child:
        if not org.is_delete:

            if not org.child:
                org_list.append(org)
            else:
                get_son(org)


@device.route("/addOrganization", methods=["POST"])
def add_organization():
    """
    Add organization information
    添加组织机构信息, post
    :return:
    """
    json_data = return_json(request)
    organization_name = json_data.get("organization_name", None)
    organization_number = json_data.get("organization_number", None)
    organization_desc = json_data.get("organization_desc", None)
    parent_id = json_data.get("parent_id", None)
    userdata = json_data.get("userdata", None)

    if parent_id and (not len(parent_id) == 32):
        code = -1
        msg = "父级组织机构id长度应为32"
        return response_tem(code=code, msg=msg, userdata=userdata)

    if not (organization_name and organization_number):
        code = -1
        msg = "组织机构名称和编号必填"
        return response_tem(code=code, msg=msg, userdata=userdata)

    try:
        if parent_id:
            parent = Organization.query.filter_by(is_delete=False, id=parent_id).first()
            if not parent:
                code = -1
                msg = "父级id不存在"
                return response_tem(code=code, msg=msg, userdata=userdata)

        param = {
            "organization_name": organization_name,
            "organization_number": organization_number,
            "organization_desc": organization_desc,
            "parent_id": parent_id if parent_id else None
        }
        organization = Organization(**param)
        db.session.add(organization)
        db.session.commit()
        code = 0
        msg = "添加成功"
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        code = -1
        msg = "添加失败"
    return response_tem(code=code, msg=msg, userdata=userdata)


# @device.route("/organization")
# def get_all_organization():
#     """
#     Get all organizational information
#     获取所有组织机构详细信息
#     :return:
#     """
#     all_info = []
#
#     try:
#         all_organization = Organization.query.filter_by(is_delete=False).all()
#         all_data = len(all_organization)
#         for org in all_organization:
#
#             org_info = {
#                 "organization_id": org.id,
#                 "organization_name": org.organization_name,
#                 "organization_number": org.organization_number,
#                 "organization_desc": org.organization_desc,
#                 "create_time": org.create_time,
#                 "update_time": org.update_time
#             }
#             camera_list = Camera.query.filter_by(is_delete=False, organization=org).all()
#             platform_list = CameraPlatform.query.filter_by(is_delete=False, organization=org).all()
#             camera_numbers = len(camera_list)
#             platform_numbers = len(platform_list)
#             org_info["camera_numbers"] = camera_numbers
#             org_info["platform_numbers"] = platform_numbers
#
#             all_info.append(org_info)
#         code = 0
#         msg = "查询成功"
#     except Exception as e:
#         logger.error(e)
#         code = -1
#         msg = "查询失败"
#         all_data = None
#     return response_tem(
#         code=code,
#         msg=msg,
#         data=all_info,
#         all_data=all_data
#     )


@device.route("/organizationInfo", methods=["POST"])
def get_organization_by_id():
    """
    Query organization information based on id
    根据id查询组织机构信息, post
    :return:
    """
    json_data = return_json(request)
    o_id = json_data.get("organization_id", None)
    user_data = json_data.get("userdata", None)

    if o_id is None:
        code = -1
        msg = "没有获取到需要查询的id"
        return response_tem(
            code=code,
            msg=msg,
            userdata=user_data
        )

    all_info = []

    try:
        organization = Organization.query.filter_by(id=o_id, is_delete=False).first()
        organization_info = {
            "organization_name": organization.organization_name,
            "organization_number": organization.organization_number,
            "organization_desc": organization.organization_desc,
            "parent_id": organization.parent_id if organization.parent_id else None,
            "parent_organization_name": organization.parent.organization_name if organization.parent_id else None,
            "create_time": organization.create_time,
            "update_time": organization.update_time
        }
        all_info.append(organization_info)

        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
    return response_tem(
        code=code,
        msg=msg,
        data=all_info,
        userdata=user_data
    )


@device.route("/modifyOrganization", methods=["POST"])
def modify_organization():
    """
    Update organization information based on ID
    根据id更新组织机构信息, post
    :return:
    """
    json_data = return_json(request)
    o_id = json_data.get("organization_id", None)
    organization_name = json_data.get("organization_name", None)
    organization_number = json_data.get("organization_number", None)
    organization_desc = json_data.get("organization_desc", None)
    parent_id = json_data.get("parent_id", None)
    userdata = json_data.get("userdata", None)

    if parent_id and (not len(parent_id) == 32):
        code = -1
        msg = "父级组织机构id长度应为32"
        return response_tem(
            code=code,
            msg=msg,
            userdata=userdata
        )

    if not (organization_name and organization_number):
        code = -1
        msg = "组织机构名称和编号必填"
        return response_tem(
            code=code,
            msg=msg,
            userdata=userdata
        )
    try:
        organization = Organization.query.filter_by(id=o_id, is_delete=False).first()
        if parent_id:
            parent_org = Organization.query.filter_by(id=parent_id, is_delete=False).first()
            if not parent_org:
                code = -1
                msg = "父级组织机构不存在或已被删除"
                return response_tem(
                    code=code,
                    msg=msg,
                    userdata=userdata
                )
        if not organization:
            code = -1
            msg = "该组织机构不存在或已被删除"
            return response_tem(
                code=code,
                msg=msg,
                userdata=userdata
            )
        organization.organization_name = organization_name
        organization.organization_number = organization_number
        organization.organization_desc = organization_desc
        organization.parent_id = parent_id if parent_id else None
        db.session.add(organization)
        db.session.commit()
        code = 0
        msg = "更新成功"
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        code = -1
        msg = "更新失败"
    return response_tem(
        code=code,
        msg=msg,
        userdata=userdata
    )


@device.route("/searchOrganization", methods=["POST"])
def search_organization():
    """
    Query organization information
    查询组织机构信息
    :return:
    """
    json_data = return_json(request)
    keywords = json_data.get("searchInfo", None)
    page = json_data.get("page", None)
    page_size = json_data.get("page_size", None)
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
            search_org_name = keywords.get("organization_name", None)
            parent_organization_id = keywords.get("parent_organization_id", None)
            is_create = keywords.get("is_create", True)
            is_desc = keywords.get("is_desc", True)

            if parent_organization_id:

                father_organization = Organization.query.filter_by(id=parent_organization_id, is_delete=False).first()
                if not father_organization:
                    code = -1
                    msg = "id:{}不存在或已被删除".format(parent_organization_id)
                    logger.error(msg)
                    return response_tem(
                        code=code,
                        msg=msg,
                        userdata=user_data
                    )
                get_son(father_organization)
                if is_create:
                    if is_desc:
                        org_list.sort(key=lambda x:x.create_time, reverse=True)
                    else:
                        org_list.sort(key=lambda x:x.create_time)
                else:
                    if is_desc:
                        org_list.sort(key=lambda x:x.update_time, reverse=True)
                    else:
                        org_list.sort(key=lambda x:x.update_time)

                pagination = paginate.Page(org_list, page, page_size)
                all_data = pagination.item_count
                all_page = pagination.last_page
                now_page = pagination.page

                for org in pagination.items:
                    org_info = {
                        "organization_id": org.id,
                        "organization_name": org.organization_name,
                        "organization_number": org.organization_number,
                        "organization_desc": org.organization_desc,
                        "create_time": org.create_time,
                        "update_time": org.update_time
                    }
                    camera_list = Camera.query.filter_by(is_delete=False, organization=org).all()
                    platform_list = CameraPlatform.query.filter_by(is_delete=False, organization=org).all()
                    camera_numbers = len(camera_list)
                    platform_numbers = len(platform_list)
                    org_info["camera_numbers"] = camera_numbers
                    org_info["platform_numbers"] = platform_numbers
                    all_info.append(org_info)
                org_list.clear()
                code = 0
                msg = "查找成功"
                return response_tem(
                    code=code,
                    msg=msg,
                    data=all_info,
                    all_data=all_data,
                    all_page=all_page,
                    page=now_page,
                    userdata=user_data
                )
            search_param = {
                "is_delete": False,
            }

            organizations = Organization.query.filter_by(**search_param).filter(
                Organization.organization_name.like("%" + search_org_name + "%") if search_org_name is not None else ""
            )
                # .paginate(page, page_size, False)
        else:
            organizations = Organization.query.filter_by(is_delete=False)
        if is_create:
            if is_desc:
                pagination = organizations.order_by(Organization.create_time.desc()).paginate(page, page_size, False)
            else:
                pagination = organizations.order_by(Organization.create_time.asc()).paginate(page, page_size, False)
        else:
            if is_desc:
                pagination = organizations.order_by(Organization.update_time.desc()).paginate(page, page_size, False)
            else:
                pagination = organizations.order_by(Organization.update_time.asc()).paginate(page, page_size, False)

        all_data = pagination.total
        all_page = pagination.pages
        now_page = pagination.page
        for org in pagination.items:
            org_info = {
                "organization_id": org.id,
                "organization_name": org.organization_name,
                "organization_number": org.organization_number,
                "organization_desc": org.organization_desc,
                "create_time": org.create_time,
                "update_time": org.update_time
            }
            camera_list = Camera.query.filter_by(is_delete=False, organization=org).all()
            platform_list = CameraPlatform.query.filter_by(is_delete=False, organization=org).all()
            camera_numbers = len(camera_list)
            platform_numbers = len(platform_list)
            org_info["camera_numbers"] = camera_numbers
            org_info["platform_numbers"] = platform_numbers
            all_info.append(org_info)
        code = 0
        msg = "查询成功"

    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
        all_data = None
        all_page = None
        now_page = None
        org_list.clear()
    return response_tem(
        code=code,
        msg=msg,
        data=all_info,
        all_data=all_data,
        all_page=all_page,
        page=now_page,
        userdata=user_data
    )


@device.route("/findSonOrganization", methods=["POST"])
def find_son_node():
    """
    Find son organization
    查找子级机构
    :return:
    """

    json_data = return_json(request)
    o_id = json_data.get("organization_id", None)
    user_data = json_data.get("userdata", None)

    if not o_id or type(o_id) is not str or not len(o_id) == 32:
        code = -1
        msg = "参数错误"
        return response_tem(
            code=code,
            msg=msg,
            userdata=user_data
        )

    all_info = []

    try:
        organization = Organization.query.filter_by(id=o_id, is_delete=False).first()

        if not organization:
            code = -1
            msg = "该组织机构不存在或已被删除"
            return response_tem(
                code=code,
                msg=msg,
                userdata=user_data
            )

        for org in organization.child:

            org_info = {
                "organization_id": org.id,
                "organization_name": org.organization_name
            }
            all_info.append(org_info)
        code = 0
        msg = "查找成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查找失败"
    return response_tem(
        code=code,
        msg=msg,
        data=all_info,
        userdata=user_data
    )


@device.route("/allOrganizations")
def get_all_organizations():
    """
    Get all the organizations for the front end to display the tree structure
    获取所有组织机构,供前端展示树状结构
    :return:
    """
    all_info = []
    try:
        organizations = Organization.query.filter_by(is_delete=False).all()

        for org in organizations:
            org_info = {
                "organization_id": org.id,
                "organization_name": org.organization_name,
                "parent_id": org.parent_id
            }
            all_info.append(org_info)
        code = 0
        msg = "查询成功"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
    return response_tem(
        code=code,
        msg=msg,
        data=all_info
    )


@device.route("/deleteOrganization", methods=["POST"])
def delete_organizations():
    """
    Delete an organization, you can delete multiple at the same time
    删除组织机构 可以是多个
    :return:
    """
    json_data = return_json(request)
    ids = json_data.get("ids", None)
    user_data = json_data.get("userdata", None)

    if (type(ids) is str and not len(ids) == 32) or \
            ids is None or len(ids) == 0:
        code = -1
        msg = "ids格式非法"
        return response_tem(
            code=code,
            msg=msg,
            userdata=user_data
        )
    if type(ids) is list:
        for _id in ids:
            if not len(_id) == 32:
                code = -1
                msg = "ids格式非法"
                return response_tem(
                    code=code,
                    msg=msg,
                    userdata=user_data
                )
    if type(ids) is str and len(ids) == 32:
        ids = [ids]
    try:
        for _id in ids:
            org = Organization.query.filter_by(is_delete=False, id=_id).first()
            if not org:
                code = -1
                msg = "id:{}不存在或已被删除".format(_id)
                logger.error(msg)
                return response_tem(
                    code=code,
                    msg=msg,
                    userdata=user_data
                )

            for childOrg in org.child:
                childOrg.is_delete = True
                db.session.add(childOrg)

            for platform in org.cameraplatforms.all():
                platform.is_delete = True
                db.session.add(platform)

            for camera in org.cameras.all():
                camera.is_delete = True
                db.session.add(camera)

            org.is_delete = True
            db.session.add(org)
        db.session.commit()
        code = 0
        msg = "删除成功"
    except Exception as e:
        db.session.rollback()
        logger.error(e)
        code = -1
        msg = "删除失败"
    return response_tem(
        code=code,
        msg=msg,
        userdata=user_data
    )


@device.route("/platformsByOrganization", methods=["POST"])
def get_platforms_by_organization():
    """
    Get platform information based on organization
    根据组织机构获取平台信息
    :return:
    """
    json_data = return_json(request)
    o_id = json_data.get("id", None)
    user_data = json_data.get("userdata", None)

    if not o_id or type(o_id) is not str or not len(o_id) == 32:
        code = -1
        msg = "参数错误"
        return response_tem(
            code=code,
            msg=msg,
            userdata=user_data
        )

    all_info = []

    try:
        organization = Organization.query.filter_by(id=o_id, is_delete=False).first()
        if not organization:
            code = -1
            msg = "id:{}不存在或已被删除".format(o_id)
            logger.error(msg)
            return response_tem(code=code, msg=msg, userdata=user_data)
        platforms = CameraPlatform.query.filter_by(is_delete=False, organization=organization).all()
        all_data = len(platforms)
        for platform in platforms:
            platform_info = {
                "platform_id": platform.id,
                "camera_platform_name": platform.camera_platform_name
            }
            all_info.append(platform_info)
        code = 0
        msg = "查询成功"
    except Exception as e:
        code = -1
        msg = "查询失败"
        all_data = None
        logger.error(e)
    return response_tem(
        code=code,
        msg=msg,
        data=all_info,
        all_data=all_data,
        userdata=user_data
    )


@device.route("/organizationTimeOrder", methods=["POST"])
def organization_time_order():
    """
    Sort by or according to the creation time or update time,
    the default is sorted according to the creation time in reverse order.
    根据创建时间或者更新时间正排序或者倒排序, 默认根据创建时间倒序排序
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
                pagination = Organization.query.filter_by(is_delete=False).order_by(Organization.create_time.desc()).\
                    paginate(page, page_size, 0)
            else:
                pagination = Organization.query.filter_by(is_delete=False).order_by(Organization.create_time.asc()).\
                    paginate(page, page_size, 0)
        else:
            if is_desc:
                pagination = Organization.query.filter_by(is_delete=False).order_by(Organization.update_time.desc()).\
                    paginate(
                    page, page_size, 0)
            else:
                pagination = Organization.query.filter_by(is_delete=False).order_by(Organization.update_time.asc()).\
                    paginate(
                    page, page_size, 0)

        all_data = pagination.total
        all_page = pagination.pages
        now_page = pagination.page

        for org in pagination.items:
            org_info = {
                "organization_id": org.id,
                "organization_name": org.organization_name,
                "organization_number": org.organization_number,
                "organization_desc": org.organization_desc,
                "create_time": org.create_time,
                "update_time": org.update_time
            }
            all_info.append(org_info)
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


@device.route("/organizationIsExist", methods=["POST"])
def accurate_query():
    """
    accurate query the organization's information
    精确查询组织机构信息,验证该组织机构名称是否存在
    :return:
    """
    json_data = return_json(request)
    organization_name = json_data.get("organization_name", None)
    user_data = json_data.get("userdata", None)
    data = None
    try:
        if not organization_name:
            code = -1
            msg = "参数错误"
            return response_tem(code=code, msg=msg, userdata=user_data, data=data)
        org = Organization.query.filter_by(organization_name=organization_name).first()
        code = 0

        if not org:
            data = 0
            msg = "该组织机构暂未添加"
        else:
            data = -1
            msg = "该组织机构已存在"
    except Exception as e:
        logger.error(e)
        code = -1
        msg = "查询失败"
        data = None
    return response_tem(
        code=code,
        msg=msg,
        data=data,
        userdata=user_data
    )
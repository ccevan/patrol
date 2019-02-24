#! python3
# __author__ = "YangJiaHao"
# date: 2018/7/18

import uuid
import json
import datetime
from loggings import logger
from app import db, scheduler
from sqlalchemy import desc, asc
from app.resources.task import task
from sqlalchemy.exc import IntegrityError
from app.forms.taskforms import AddTaskForm
from flask import request, jsonify, Response
from app.resources.task.assign_task import TaskStartHelper, task_helper, zabbix, task_job
from app.models.models import Task, TaskItemRelationship, Channel, Item


# Camera, TaskChannelRelationship


@task.route('/test')
def test():
    # 测试任务相关功能

    # items = ["rollScreen", "occlusion", "noise", "fuzziness", "frozen", "dark", "crossGrain", "content",
    #          "chromaticColor", "brightness", "move", "shake", "delay", "packetLossRate", "timeCalibration"]
    # for each in items:
    from flask import jsonify
    try:
        item = Item()
        item.item_name = "kakaka"
        item.item_type = 1
        db.session.add(item)
        db.session.flush()
        item = Item()
        item.item_name = "bibibi"
        item.item_type = 1
        db.session.add(item)
        # chan = Channel()
        # chan.camera_id ="607f4e0121534faa9ae77f5357f76926"
        # db.session.add(chan)

        db.session.commit()

    except Exception as e:
        # db.session.rollback()
        return str(e)
    # data = assign_task('796f97669f95489c99f846605c439f8f')
    # data = finish_network_diagnosis("df7f94cc70a340eb8fbcb1603cc86393")
    # video_quality_diagnosis('',2)
    #
    # cookie = request.cookies
    # res = jsonify(cookie)
    # response = make_response('hello')
    # response.set_cookie("name","admin")

    return "OK"


@task.route('/addTask', methods=['POST'])
def add_task():
    """
    添加任务，保存任务信息，加入任务调度器。
    """
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    form = AddTaskForm.from_json(request.json)
    userdata = request.json.get('userdata')
    if not form.validate():
        return render_response(-1, data=form.errors, userdata=userdata)

    task = Task()
    task_id = uuid.uuid4().hex
    task.id = task_id
    task.task_name = form.task_name.data
    task.task_type = form.task_type.data
    task.hours = form.hours.data
    task.minutes = form.minutes.data
    # task.seconds = form.seconds.data
    task.day_of_week = form.day_of_week.data
    task.day_of_month = form.day_of_month.data
    task.task_priority = form.task_priority.data
    task.task_start_date = form.task_start_date.data
    task.task_end_date = form.task_end_date.data
    task.task_desc = form.task_desc.data
    task.alarm_mode = form.alarm_mode.data
    # task.creator_id = task.modifier_id = form.user_id.data
    # task.creator_name = task.modifier_name = form.user_name.data
    task.task_status = 0
    task.system_id = form.system_id.data

    channels_info = form.channels.data

    if not channels_info:
        return render_response(-1, msg="no channel selected.")

    # 获取组织机构下所有相机id
    for channel_info in channels_info:
        channel = Channel()
        channel.task_id = task_id
        channel.channel_id = channel_info.get("channel_id")
        channel.channel_number = channel_info.get("channel_number")
        channel.organization_id = channel_info.get("organization_id")
        channel.device_id = channel_info.get("device_id")
        channel.is_platform = channel_info.get("is_platform")
        channel.platform_id = channel_info.get("platform_id")
        channel.platform_host = channel_info.get("platform_host")
        channel.platform_port = channel_info.get("platform_port")
        channel.platform_user = channel_info.get("platform_user")
        channel.platform_password = channel_info.get("platform_password")
        db.session.add(channel)

    # 创建 任务与检测项目关系表
    items = form.items.data
    task_item_relationships = []
    for k, v in items.items():
        if v is not None:
            item = Item.query.filter_by(item_name=k).first()
            if not item:
                msg = "item name not exist: {}".format(k)
                return render_response(code=-1, userdata=userdata, msg=msg)
            relationship = TaskItemRelationship(task_id=task.id,
                                                item_id=item.id,
                                                threshold=v)
            task_item_relationships.append(relationship)
    task.items = task_item_relationships

    # 添加任务到 任务调度器
    if int(task.task_type) == 1:  # 如果为 一次执行
        try:  # 解析时间
            time_str = "{} {}:{}".format(form.task_start_date.data,
                                         task.hours, task.minutes)
            run_date = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")
            if run_date.timestamp() < datetime.datetime.now().timestamp():
                #  设置 misfire_grace_time
                if -1 < datetime.datetime.now().timestamp() - run_date.timestamp() < 120:
                    run_date = datetime.datetime.now() + datetime.timedelta(seconds=1)

                else:
                    msg = "task run time is missed."  # 执行时间已经错过
                    return render_response(code=-1, msg=msg, userdata=userdata)

        except Exception as e:
            msg = "time format error: {}".format(e)
            logger.error(msg)
            return render_response(code=-1, msg=msg, userdata=userdata)

        job = scheduler.add_job(id=task_id,
                                func=task_job,
                                args=(task_id,),
                                replace_existing=True,
                                trigger='date',
                                run_date=run_date)
    else:
        task.task_end_date = None
        # APScheduler day_of_week 从0开始,添加时需要减一。
        day_of_weeks = task.day_of_week or None
        if day_of_weeks and type(day_of_weeks) == str:
            day_of_weeks = list(map(lambda x: int(x) - 1, task.day_of_week.split(",")))
            day_of_weeks = ",".join(map(str, day_of_weeks))
        job = scheduler.add_job(id=task_id,
                                func=task_job,
                                args=(task_id,),
                                replace_existing=True,
                                trigger='cron',
                                day=task.day_of_month or None,
                                day_of_week=day_of_weeks,
                                hour=task.hours,
                                minute=task.minutes,
                                start_date=task.task_start_date,
                                end_date=task.task_end_date
                                )

    try:
        db.session.add(task)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        try:
            job.remove()
        except Exception:
            pass
        # scheduler.remove_job(id=task.id)
        logger.error("add task error: {}".format(e))
        return render_response(code=-1, msg='Integrity Error.', userdata=userdata)

    except Exception as e:
        db.session.rollback()
        try:
            job.remove()
        except:
            pass
        # scheduler.remove_job(id=task.id)
        logger.error("add task error: {}".format(e))
        return render_response(code=-1, msg='Database error.', userdata=userdata)

    msg = "next run time: {}".format(job.next_run_time)
    return render_response(code=0, userdata=userdata, msg=msg)


@task.route('/updateTask', methods=['POST'])
def update_task():
    """
    更新任务
    :return:
    """
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")
    form = AddTaskForm.from_json(request.json)
    task_id = request.json.get("task_id")
    userdata = request.json.get('userdata')
    # 表单验证
    if not form.validate():
        return render_response(-1, data=form.errors, userdata=userdata)

    # 任务id验证
    if not request.json.get('task_id'):
        msg = "task id is required"
        return render_response(-1, msg=msg, userdata=userdata)

    task = Task.query.get(task_id)
    # 任务未找到
    if not task:
        render_response(-1, msg='task not exist.')

    task.task_name = form.task_name.data
    task.task_type = form.task_type.data
    task.hours = form.hours.data
    task.minutes = form.minutes.data
    # task.seconds = form.seconds.data
    task.day_of_week = form.day_of_week.data
    task.day_of_month = form.day_of_month.data
    task.task_priority = form.task_priority.data
    task.task_start_date = form.task_start_date.data
    task.task_end_date = form.task_end_date.data
    task.task_desc = form.task_desc.data
    task.alarm_mode = form.alarm_mode.data
    # task.modifier_id = form.user_id.data
    # task.modifier_name = form.user_name.data
    task.task_status = 0

    channels_info = form.channels.data

    if not channels_info:
        return render_response(-1, msg="no channel selected.")

    channels_old = Channel.query.filter_by(task_id=task.id).all()
    for channel in channels_old:
        channel.is_delete = True
        db.session.add(channel)

    for channel_info in channels_info:
        channel = Channel()
        channel.task_id = task_id
        channel.channel_id = channel_info.get("channel_id")
        channel.channel_number = channel_info.get("channel_number")
        channel.organization_id = channel_info.get("organization_id")
        channel.device_id = channel_info.get("device_id")
        channel.is_platform = channel_info.get("is_platform")
        channel.platform_id = channel_info.get("platform_id")
        channel.platform_host = channel_info.get("platform_host")
        channel.platform_port = channel_info.get("platform_port")
        channel.platform_user = channel_info.get("platform_user")
        channel.platform_password = channel_info.get("platform_password")
        db.session.add(channel)

    # 创建 任务与检测项目关系表
    items = form.items.data
    task_item_relationships = []
    for k, v in items.items():
        if v is not None:
            item = Item.query.filter_by(item_name=k).first()
            if not item:
                msg = "item name not exist: {}".format(k)
                return render_response(code=-1, userdata=userdata, msg=msg)
            relationship = TaskItemRelationship(task_id=task.id,
                                                item_id=item.id,
                                                threshold=v)
            task_item_relationships.append(relationship)
    task.items = task_item_relationships

    # 添加任务到 任务调度器
    if int(task.task_type) == 1:  # 如果为 一次执行
        try:
            time_str = "{} {}:{}".format(form.task_start_date.data,
                                         task.hours, task.minutes)
            run_date = datetime.datetime.strptime(time_str, "%Y-%m-%d %H:%M")

            # if run_date.timestamp() < datetime.datetime.now().timestamp():
            #      设置 misfire_grace_time
            # if -1 < datetime.datetime.now().timestamp() - run_date.timestamp() < 120:
            #     run_date = datetime.datetime.now() + datetime.timedelta(seconds=1)
            # else:
            #     msg = "task run time is missed."  # 执行时间已经错过
            #     return render_response(code=-1, msg=msg, userdata=userdata)

        except Exception as e:
            logger.error("update task time error:{}".format(e))
            msg = "time format error: {}".format(e)
            return render_response(code=-1, msg=msg, userdata=userdata)
        # 添加新的任务，旧的任务被覆盖。
        job = scheduler.add_job(id=task_id,
                                func=task_job,
                                args=(task_id,),
                                replace_existing=True,
                                trigger='date',
                                run_date=run_date)
    else:
        # APScheduler day_of_week 从0开始,添加时需要减一。
        day_of_weeks = task.day_of_week or None
        if day_of_weeks and type(day_of_weeks) == str:
            day_of_weeks = list(map(lambda x: int(x) - 1, task.day_of_week.split(",")))
            day_of_weeks = ",".join(map(str, day_of_weeks))

        # 添加新的任务，旧的任务被覆盖。
        job = scheduler.add_job(id=task_id,
                                func=task_job,
                                args=(task_id,),
                                replace_existing=True,
                                trigger='cron',
                                day=task.day_of_month,
                                day_of_week=day_of_weeks or None,
                                hour=task.hours,
                                minute=task.minutes
                                )
    # if job.next_run_time < datetime.datetime.now():
    #     pass

    try:
        db.session.add(task)
        db.session.commit()

    except IntegrityError as e:
        db.session.rollback()
        try:
            scheduler.remove_job(id=task.id)
        except:
            pass
        logger.error("update task error", e)
        return render_response(code=-1, msg='Integrity error.', userdata=userdata)

    except Exception as e:
        db.session.rollback()
        try:
            scheduler.remove_job(id=task.id)
        except:
            pass
        logger.error("update task error", e)
        return render_response(code=-1, msg='database error', userdata=userdata)

    msg = "next run time: {}".format(job.next_run_time)
    return render_response(code=0, userdata=userdata, msg=msg)


@task.route('/stopTask', methods=["POST"])
def stop_task():
    """
    暂停正在执行的任务
    """
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    userdata = request.json.get('userdata')

    task_ids = request.json.get('task_id')
    if not task_ids:
        return render_response(-1, msg="task_id is required.")

    if type(task_ids) == str:
        task_ids = [task_ids]

    for task_id in task_ids:
        task = Task.query.get(task_id)
        if not task:
            return render_response(code=-1, msg="task not found.", userdata=userdata)

        try:  # 停止 zabbix
            zabbix.stop(task_id)
        except:
            pass
        try:  # 停止 任务调度
            scheduler.pause_job(task_id)
        except:
            pass

        task.task_status = 2  # 任务状态0表示停止
        try:
            db.session.add(task)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            return render_response(code=-1, msg="database error.", userdata=userdata)

    return render_response(code=0, userdata=userdata)


@task.route('/startTask', methods=["POST"])
def start_task():
    """
    启动已经暂停的任务
    """
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    userdata = request.json.get('userdata')

    task_ids = request.json.get('task_id')
    if not task_ids:
        return render_response(-1, msg="task_id is required.")

    if type(task_ids) == str:
        task_ids = [task_ids]

    for task_id in task_ids:
        task = Task.query.get(task_id)

        if not task:
            msg = "task not found."
            return render_response(code=-1, msg=msg, userdata=userdata)

        task_helper.assign_task(task.id)

        try:
            scheduler.resume_job(task_id)
        except Exception as e:
            logger.error(e)
            msg = "Startup failed. task may be already finished."
            # return render_response(code=-1, userdata=userdata, msg=msg)

        task.task_status = 1  # 任务状态1表示已启动
        try:
            db.session.add(task)
            db.session.commit()
        except Exception as e:
            logger.error(e)
            return render_response(code=-1, msg="database error.", userdata=userdata)

    return render_response(code=0, userdata=userdata)


@task.route("/getTaskById", methods=["POST"])
def get_task_by_id():
    """
    根据任务id获取任务的详情。
    """
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    task_id = request.json.get("task_id")
    userdata = request.json.get("userdata")
    task = Task.query.get(task_id)

    if not task:
        msg = "task not exist."
        return render_response(code=1, msg=msg, userdata=userdata)

    # 找出任务下的通道
    channels = Channel.query.filter_by(task_id=task_id).all()

    channels_info = []
    # 查询并生成数据。
    try:
        for channel in channels:
            channel_info = dict()
            channel_info["channel_id"] = channel.channel_id
            channel_info["channel_number"] = channel.channel_number
            channel_info["platform_id"] = channel.platform_id
            channels_info.append(channel_info)

            # if each.channel.camera.cameraplatform_id:
            #     channel["platform_name"] = each.channel.camera.cameraplatform.camera_platform_name
            # else:
            #     channel["platform_name"] = None
            # channel["create_time"] = each.channel.create_time.strftime("%Y-%m-%d %H:%M:%S")
            # channel["update_time"] = each.channel.update_time.strftime("%Y-%m-%d %H:%M:%S")
            # channel["creator"] = 'admin'
            # channel["organization_id"] = each.channel.camera.organization_id
            # if each.channel.camera.organization_id:
            #     channel["organization_name"] = each.channel.camera.organization.organization_name
            # else:
            #     channel["organization_name"] = None

        # 找出任务下的检测项目
        items = {}
        items_rels = task.items
        for each in items_rels:
            items[each.item.item_name] = each.threshold

        # 构造返回json
        task_dict = task.to_json()
        task_dict["start_time"] = task.hours + ':' + task.minutes
        task_dict["userdata"] = userdata
        task_dict["channels"] = channels_info
        task_dict["items"] = items
        task_dict["alarm_mode"] = task.alarm_mode
        if task.task_start_date:
            task_dict["task_start_date"] = task.task_start_date.strftime("%Y-%m-%d")
        if task.task_end_date:
            task_dict["task_end_date"] = task.task_end_date.strftime("%Y-%m-%d")
    except Exception as e:
        logger.error("get task by id error:{}".format(e))
        return render_response(-1, msg="Failed to generate data.", userdata=userdata)

    return render_response(0,
                           data=task_dict,
                           userdata=userdata)


@task.route("/searchTask", methods=["POST"])
def search_task_list():
    """搜索任务，多条件搜索"""
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    data_list = list()
    task_info = request.json

    page_size = int(task_info.get("page_size", 20) or 20)
    pagenum = int(task_info.get("page", 1) or 20)
    alarm_mode = task_info.get("alarm_mode")
    userdata = task_info.get("userdata")
    task_name = task_info.get("task_name")
    task_priority = task_info.get("priority")
    task_type = task_info.get("task_type")
    task_status = task_info.get("task_status")
    sort_field = task_info.get('sort_field') or "update_time"
    sort_order = task_info.get("sort_order") or "desc"  # ase desc

    # 添加 filter_by 过滤参数
    kwargs = dict()
    try:
        task_priority = int(task_priority)
    except:
        task_priority = None

    if task_priority is not None:
        kwargs['task_priority'] = task_priority
    if alarm_mode:
        kwargs['alarm_mode'] = alarm_mode
    if task_type:
        kwargs['task_type'] = task_type
    if task_status:
        kwargs['task_status'] = task_status

    # 添加 filter 过滤参数
    args = []
    if task_name:
        args.append(Task.task_name.like("%" + task_name + "%"))

    # 排序方式
    if sort_order == 'asc':
        sort_order = asc
    else:
        sort_order = desc

    # 排序字段
    if sort_field == "start_time":
        sort_field = [sort_order(Task.hours), sort_order(Task.minutes)]
    elif sort_field == "start_date":
        sort_field = [sort_order(Task.task_start_date)]
    elif sort_field == "end_date":
        sort_field = [sort_order(Task.task_end_date)]
    else:
        sort_field = [sort_order(Task.create_time)]

    try:
        pagination = Task.query.filter_by(is_delete=False, **kwargs). \
            filter(*args).order_by(*sort_field). \
            paginate(pagenum, per_page=page_size, error_out=False)

        taskinfo_list = pagination.items

        for taskinfo in taskinfo_list:
            task_dict = taskinfo.to_json()
            task_dict["alarm_mode"] = taskinfo.alarm_mode
            task_dict["start_time"] = taskinfo.hours + ':' + taskinfo.minutes
            task_dict["userdata"] = userdata
            if taskinfo.task_start_date:
                task_dict["task_start_date"] = taskinfo.task_start_date.strftime("%Y-%m-%d")
            if taskinfo.task_end_date:
                task_dict["task_end_date"] = taskinfo.task_end_date.strftime("%Y-%m-%d")
            data_list.append(task_dict)

    except Exception as e:
        # 接口调用失败
        logger.error("search task error:{}".format(e))
        msg = "generate data error."
        return render_response(-1, msg=msg, userdata=userdata)

    return render_response(0,
                           data=data_list,
                           page=pagination.page,
                           all_page=pagination.pages,
                           all_data=pagination.total,
                           userdata=userdata)


@task.route("/deleteTask", methods=["PUT", "POST"])
def delete_task():
    """根据id删除任务"""
    if not request.content_type == 'application/json':
        return render_response(-1, msg="Content-type must be application/json.")

    task_info = request.json
    task_ids = task_info.get("task_id")
    if not task_ids:
        return render_response(-1, msg="task_id is required.")

    userdata = task_info.get("userdata")
    logger.info((task_ids, userdata))

    if isinstance(task_ids, str):
        task_ids = [task_ids]

    # 对task_id进行查询
    try:
        for task_id in task_ids:
            taskinfo = Task.query.filter((Task.id == task_id) &
                                         (Task.is_delete == False)).first()
            if taskinfo is None:
                logger.error("task not exist.")
                return render_response(-1, userdata=userdata, msg='task not exist.')
            taskinfo.is_delete = True
            db.session.add(taskinfo)

            # 删除调度器中的任务
            try:
                scheduler.remove_job(task_id)
            except:
                pass

        db.session.commit()

    except Exception as e:
        # 接口调用失败
        logger.error("task delete error:{}".format(e))
        db.session.rollback()
        msg = "database delete error."
        return render_response(-1, msg=msg, userdata=userdata)
    # logger.info("删除任务成功")
    return render_response(0, userdata=userdata, msg="delete success.")


def render_response(code=0, data=None, msg=None, page=None,
                    all_page=None, all_data=None, userdata=None):
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

    res = json.dumps(res, default=str)
    return Response(response=res, status=200, mimetype="application/json")
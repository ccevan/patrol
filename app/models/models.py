from app import db
from datetime import datetime
import uuid
# from werkzeug.security import check_password_hash, generate_password_hash


def gen_id():
    return uuid.uuid4().hex


class BaseModel(object):
    """模型基类，为每个模型补充创建时间与更新时间"""

    create_time = db.Column(db.DateTime, default=datetime.now)  # 记录的创建时间
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # 记录的更新时间

    def add(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def rollback(self):
        db.session.rollback()


class Channel(BaseModel, db.Model):
    __tablename__ = "tbchannel"

    id = db.Column(db.String(32),default=gen_id,nullable=False, primary_key=True)

    channel_id = db.Column(db.String(36)) # 通道id  36
    channel_number = db.Column(db.String(20))  # 通道号
    organization_id = db.Column(db.String(36))  # 组织机构id  36
    device_id = db.Column(db.String(36)) # 设备id  36
    task_id = db.Column(db.String(32)) # 任务id  32
    platform_id = db.Column(db.String(36))  #平台id 36
    platform_host = db.Column(db.String(20))  # 平台主机地址
    platform_port = db.Column(db.String(8))  # 平台主机端口
    platform_user = db.Column(db.String(20))  # 平台用户名
    platform_password = db.Column(db.String(36))  # 平台用户密码
    is_platform = db.Column(db.Boolean, default=True, nullable=False)  # 是否是平台 ture or false
    is_delete = db.Column(db.Boolean, default=False, nullable=False)  # 修改任务的时候把此字段改成True，然后重新写入数据

    def __repr__(self):
        return "<Channel %r>" % self.channel_id


class TaskItemRelationship(db.Model):
    __tablename__ = "tbtaskitemrel"
    task_id = db.Column(db.String(32), db.ForeignKey("tbtask.id"), primary_key=True)
    item_id = db.Column(db.String(32), db.ForeignKey("tbitem.id"), primary_key=True)
    threshold = db.Column(db.Integer)  # 阈值
    timestamp = db.Column(db.DateTime, default=datetime.now)


class FaultItemRelationship(db.Model):
    __tablename__ = "tbfaultitemrel"
    fault_id = db.Column(db.String(32), db.ForeignKey("tbfault.id"), primary_key=True)
    item_id = db.Column(db.String(32), db.ForeignKey("tbitem.id"), primary_key=True)
    threshold = db.Column(db.Integer)  # 阈值
    timestamp = db.Column(db.DateTime, default=datetime.now)


class Task(BaseModel, db.Model):
    __tablename__ = "tbtask"

    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)
    task_name = db.Column(db.String(64), nullable=False)
    task_type = db.Column(db.Integer, nullable=False)  # 1-一次执行 2-每天执行 3-每周之行 4-每月执行
    minutes = db.Column(db.String(32), default="*")
    hours = db.Column(db.String(32), default="*")
    day_of_month = db.Column(db.String(32), default="*")
    day_of_week = db.Column(db.String(32), default="*")
    task_priority = db.Column(db.Integer, nullable=False)  # 1 低 2 中 3 高
    task_status = db.Column(db.Integer)  # 0 未执行 1 正在执行 2 已暂停 3 已完成
    task_desc = db.Column(db.String(200))
    alarm_mode = db.Column(db.Integer)  # 1 本地报警  2 短信报警  3 邮件报警  4 微信报警
    task_start_date = db.Column(db.Date)  # 任务起始时间
    task_end_date = db.Column(db.Date)  # 任务结束时间
    system_id = db.Column(db.String(36))  # 系统id
    is_delete = db.Column(db.Boolean, default=False, nullable=False)
    run_num = db.Column(db.Integer, default=0)  # 该任务在本月内执行的次数
    items = db.relationship("TaskItemRelationship", foreign_keys=[TaskItemRelationship.task_id], backref=db.backref("task", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")
    faults = db.relationship("Fault", backref="task", lazy="dynamic")
    # channels = db.relationship("Channel", backref="task", lazy="dynamic")

    def to_json(self):
        json_task = {
            "task_id": self.id,
            "task_name": self.task_name,
            "task_type": self.task_type,
            "minutes": self.minutes,
            "hours": self.hours,
            "day_of_month": self.day_of_month,
            "day_of_week": self.day_of_week,
            "task_priority": self.task_priority,
            "task_status": self.task_status,
            "task_desc": self.task_desc,
            "task_start_date": self.task_start_date,
            "task_end_date": self.task_end_date,
            "create_time": self.create_time,
            "update_time": self.update_time
        }
        return json_task

    def __repr__(self):
        return "<TaskName %r>" % self.task_name


class Item(BaseModel, db.Model):
    __tablename__ = "tbitem"

    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)
    item_name = db.Column(db.String(20), nullable=False)
    item_type = db.Column(db.Integer, nullable=False)  # 检测项类型 1 视频质量 2 网络参数 3 时间校准
    item_desc = db.Column(db.String(400))
    is_delete = db.Column(db.Boolean, nullable=False, default=False)
    tasks = db.relationship("TaskItemRelationship", foreign_keys=[TaskItemRelationship.item_id], backref=db.backref("item", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")
    faults = db.relationship("FaultItemRelationship", foreign_keys=[FaultItemRelationship.item_id], backref=db.backref("item", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")

    def to_json(self):
        json_item = {
            "id": self.id,
            "item_name": self.item_name,
            "item_type": self.item_type,
            "item_desc": self.item_desc
        }
        return json_item

    def __repr__(self):

        return "<ItemName %r>" % self.item_name


class Fault(BaseModel, db.Model):
    __tablename__ = "tbfault"

    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)
    pic_url = db.Column(db.String(128))
    video_url = db.Column(db.String(128))
    task_id = db.Column(db.String(32), db.ForeignKey("tbtask.id"))
    channel_id = db.Column(db.String(36))
    type1 = db.Column(db.Boolean, default=False)  # 值为true 画面异常
    type2 = db.Column(db.Boolean, default=False)  # 值为true 网络参数问题
    type3 = db.Column(db.Boolean, default=False)  # 值为true 时间异常
    status = db.Column(db.Integer, default=0)  # 0未处理 1 已处理 2 以忽略 3 误诊断
    is_delete = db.Column(db.Boolean, nullable=False, default=False)
    items = db.relationship("FaultItemRelationship", foreign_keys=[FaultItemRelationship.fault_id], backref=db.backref("fault", lazy="joined"), lazy="dynamic", cascade="all, delete-orphan")

    def __repr__(self):
        return "<Fault %r>" % self.id


class FaultCount(BaseModel, db.Model):
    """
    记录出故障的相机数量和故障率
    """
    __tablename__ = "tbfaultcount"
    id = db.Column(db.String(32), default=gen_id, nullable=False, primary_key=True)
    date = db.Column(db.String(64))  # 出错日期 格式是字符串 "2018-09"
    num = db.Column(db.Integer, default=0)  # 出故障的相机数量
    rate = db.Column(db.Integer, default=0)  # 相机的故障率
    work_num = db.Column(db.Integer, default=0)  # 任务的每月执行数量
    processed = db.Column(db.Integer, default=0)  # 故障已处理的数量
    misdiagnosis = db.Column(db.Integer, default=0)  # 故障误诊断的数量
    ignore = db.Column(db.Integer, default=0)  # 故障忽略的个数
    unprocessed = db.Column(db.Integer, default=0) # 故障未处理的个数


    def __repr__(self):
        return "<FaultCount %r>" % self.date

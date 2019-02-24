from wtforms import Form, StringField, IntegerField, DateTimeField, \
    ValidationError, Field, widgets, FloatField, BooleanField, DateField
from wtforms.validators import optional, length, number_range, Length,data_required
import wtforms_json

wtforms_json.init()
from wtforms_json import FieldList, FormField

DictField = StringField


class Item(Form):
    fuzziness = IntegerField('模糊度 0-99', [optional(), number_range(min=0, max=99)])
    content = IntegerField('内容有效  0-99', [optional(), number_range(min=0, max=99)])
    brightness = IntegerField('过亮 0-99', [optional(), number_range(min=0, max=99)])
    rollScreen = IntegerField('条纹滚屏 0-99', [optional(), number_range(min=0, max=99)])
    chromaticColor = IntegerField('偏色度量0-99', [optional(), number_range(min=0, max=99)])
    noise = IntegerField('噪声0-99', [optional(), number_range(min=0, max=99)])
    dark = IntegerField('过暗0-99', [optional(), number_range(min=0, max=99)])

    signal = IntegerField('信号丢失', [optional(), number_range(min=0, max=1)])
    occlusion = IntegerField('遮挡', [optional(), number_range(min=0, max=1)], )
    crossGrain = IntegerField('固定横纹', [optional(), number_range(min=0, max=1)])
    frozen = IntegerField('画面冻结', [optional(), number_range(min=0, max=1)])
    move = IntegerField('相机移动', [optional(), number_range(min=0, max=1)])
    shake = IntegerField('相机抖动', [optional(), number_range(min=0, max=1)])
    timeCalibration = IntegerField('时间校准', [optional(), number_range(min=0, max=1)])

    networkDelay = FloatField('网络延迟', [optional()])
    delay = FloatField('网络延迟', [optional()])
    packetLossRate = IntegerField('丢包率', [optional(), number_range(min=0, max=99)])

class Channel(Form):
    channel_id = StringField("") # 通道id  36
    channel_number = StringField("")  # 通道号
    organization_id = StringField("")  # 组织机构id  36
    device_id = StringField("")
    is_platform = BooleanField("")  # 设备id  36
    platform_id = StringField("")  # 平台id 36
    platform_host = StringField("")  # 平台主机地址
    platform_port = IntegerField("")  # 平台主机端口
    platform_user = StringField("")  # 平台用户名
    platform_password = StringField("")  # 平台用户密码


class AddTaskForm(Form):
    task_name = StringField('', [data_required(), length(min=1, max=50)])
    task_type = IntegerField('', [data_required(), number_range(min=1, max=5)])

    hours = StringField('', [data_required(), length(1, 36)])
    minutes = StringField('', [data_required(), length(1, 36)])
    seconds = StringField('', [optional(), length(1, 36)])
    day_of_week = StringField('', [optional(), length(1, 36)])
    day_of_month = StringField('', [optional(), length(1, 36)])

    alarm_mode = IntegerField('', [data_required(), number_range(min=0, max=5)], default=1)
    task_priority = IntegerField('', [data_required(), number_range(min=0, max=5)])
    task_start_date = DateField('', [optional()])
    task_end_date = DateField('', [optional()])
    task_desc = StringField('', [optional(), length(0, 200)])

    groups = FieldList(StringField('', [optional(), Length(min=32, max=32)]))
    organizations = FieldList(StringField('', [optional(), Length(min=32, max=32)]))

    # items = StringField('',[required])
    items = FormField(Item)
    channels = FieldList(FormField(Channel))

    # user_id = StringField('', [optional()])
    # user_name = StringField('', [optional()])
    system_id = StringField('',[optional(),Length(min=36,max=36)])


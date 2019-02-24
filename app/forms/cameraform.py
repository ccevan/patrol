from wtforms import StringField, SubmitField, IntegerField, BooleanField
from wtforms.validators import Length, Email, DataRequired, Optional, IPAddress, NumberRange
import wtforms_json

wtforms_json.init()
from wtforms_json import Form


class CameraForm(Form):
    camera_name = StringField('', [DataRequired(), Length(min=1, max=40)])
    camera_manufacturer = StringField('', [Optional(), Length(min=1, max=20)])
    camera_channel = StringField('', [Optional(), Length(min=1, max=40)])
    camera_ip = StringField('', [IPAddress()])
    camera_port = IntegerField('', [NumberRange(0, 65535)])
    camera_account = StringField('', [Optional(), Length(min=1, max=20)])
    camera_password = StringField('', [Optional(), Length(min=1, max=40)])
    camera_desc = StringField('', [Optional(), Length(min=1, max=400)])
    camera_status = IntegerField('')

    gb_number = StringField('')
    registration_period = IntegerField('')
    heartbeat_timeout_secs = IntegerField('')
    heartbeat_timeout_times = IntegerField('')
    cameragroup_id = StringField('', [Optional(), Length(min=32, max=32)])
    cameraprotocol_id = StringField('', [Optional(), Length(min=32, max=32)])
    cameratype_id = StringField('', [Optional(), Length(min=32, max=32)])
    organization_id = StringField('', [Optional(), Length(min=32, max=32)])
    cameraplatform_id = StringField('', [Optional(), Length(min=32, max=32)])


class ChannelForm(Form):
    camera_id = StringField('', [Length(min=32, max=32)])
    channel_name = StringField('', [DataRequired()])
    channel_number = IntegerField('', [DataRequired()])
    gb_number = StringField('', [DataRequired()])
    yun_tai = IntegerField('', [], default=0)
    status = IntegerField('', [], default=0)
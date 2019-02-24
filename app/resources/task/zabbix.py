#! python3
# __author__ = "YangJiaHao"
# date: 2018/8/9

from loggings import logger
from pyzabbix import ZabbixAPI, ZabbixAPIException
from collections import namedtuple


class AssignZabbixTask(object):
    def __init__(self, app=None):
        """
        :param zabbix_ip: string, zabbix 服务器ip
        :param username: string, zabbix 用户名
        :param password: string, zabbix 密码
        """
        # 登录zabbix
        self.app = app
        self.task_id = None
        if app:
            self.init_app(self.app)

    def init_app(self, app):
        """
        初始化配置。
        :param app:
        :return:
        """
        self.app = app
        zabbix_ip = self.app.config.get("ZABBIX_IP")
        username = self.app.config.get('ZABBIX_USERNAME', "admin")
        passwd = self.app.config.get('ZABBIX_PASSWD', "zabbix")
        self.zabbix = ZabbixAPI("http://" + zabbix_ip)
        self.zabbix.login(username, passwd)

        self.base_template_id = self.__get_base_template_id()

    def problem(self, task_id):
        """
        获取出问题的主机和时间
        :param task_id:
        :return: namedtuple("problem_hosts", ['delay', 'loss'])
        """
        # 问题主机
        host = namedtuple("host", ['id', 'clock'])
        problem_hosts = namedtuple("problem_hosts", ['delay', 'loss'])
        problem_hosts.delay = []
        problem_hosts.loss = []

        groupid = self.__get_groupid(task_id)
        # 获取网络延迟超时的主机
        params = {
            # "output": "extend",
            "output": ["eventid", "object", "objectid", "r_eventid", "clock"],
            "groupids": [groupid],
            # "select_acknowledges": "extend",
            "tags": [{'tag': 'item', 'value': '0'}],  # 触发器tag item:0 表示网络延迟
            "selectTags": "extend",
            "value": 1,
            # "selectHosts": ["hostid", "host", "status"]
            "selectHosts": "extend"
        }
        res = self.zabbix.event.get(**params)
        for event in res:
            if event['r_eventid'] == '0':  # 排除已经恢复的故障。
                host.id = event["hosts"][0]["host"][-32:]
                host.clock = event["clock"]
                problem_hosts.delay.append(host)

        # 获取丢包率过高的主机
        params["tags"] = [{'tag': 'item', 'value': '1'}]  # 触发器tag item:1 表示丢包率
        res = self.zabbix.event.get(**params)
        for event in res:
            if event['r_eventid'] == '0':
                host.id = event["hosts"][0]["host"][-32:]
                host.clock = event["clock"]
                problem_hosts.loss.append(host)

        return problem_hosts

    def add(self, task_id, delay, loss, camera_list):
        """
        :param task_id: string,
        :param camera_list: dict
        :return:
        """
        if not self.base_template_id:
            raise ZabbixAPIException('base template not exist, please create firse.')

        self.task_id = task_id
        groupid = self.__create_hostgroup()

        try:
            template_id = self.__create_template(groupid)
        except Exception as e:
            self.zabbix.hostgroup.delete(groupid)  # 回滚
            raise ZabbixAPIException('create template error:{}'.format(e))

        try:
            self.__create_trigger(delay, loss)
        except Exception as e:
            self.zabbix.template.delete(template_id)  # 回滚
            self.zabbix.hostgroup.delete(groupid)
            raise ZabbixAPIException('create trigger error:{}'.format(e))

        try:
            self.__create_hosts(groupid, template_id, camera_list)
        except Exception as e:
            self.zabbix.template.delete(template_id)  # 回滚
            self.zabbix.hostgroup.delete(groupid)  # trigger 自动删除。
            raise ZabbixAPIException("create host error:{}".format(e))

    def stop(self, task_id):
        # 停用主机组的所有主机
        try:
            groupid = self.__get_groupid(task_id)
            if not groupid:
                raise ZabbixAPIException('no found groupid.')
            hosts = self.zabbix.host.get(groupids=groupid, output='hostid')
            if hosts:
                self.zabbix.host.massupdate(hosts=hosts, status=1)
            else:
                raise ZabbixAPIException('no host found, groupid: {}'.format(groupid))
        except Exception as e:
            raise ZabbixAPIException("stop host error: {}".format(e))

    def start(self, task_id):
        # 启用主机组内的所有主机
        try:
            groupid = self.__get_groupid(task_id)
            if not groupid:
                raise ZabbixAPIException('no found groupid.')
            hosts = self.zabbix.host.get(groupids=groupid, output='hostid')
            if hosts:
                self.zabbix.host.massupdate(hosts=hosts, status=0)
            else:
                raise ZabbixAPIException('no host found, groupid: {}'.format(groupid))

        except Exception as e:
            raise ZabbixAPIException("start host error: {}".format(e))

    def delete(self, task_id):
        """
        删除主机组，模版和主机
        :param groupid:
        :return:
        """
        try:
            groupid = self.__get_groupid(task_id)
            if not groupid:
                raise ZabbixAPIException('groupid not found.')
            # 根据主机组删除主机
            hosts = self.zabbix.host.get(groupids=groupid, output='hostid')
            if hosts:
                hostids = [host['hostid'] for host in hosts]
                self.zabbix.host.delete(*hostids)

            # 根据主机组查询并删除模版
            templates = self.zabbix.template.get(groupids=groupid, output='templateid')
            if templates:
                templateids = [template['templateid'] for template in templates]
                self.zabbix.template.delete(*templateids)
            # 删除主机组
            self.zabbix.hostgroup.delete(groupid)
        except Exception as e:
            raise ZabbixAPIException("delete error: {}".format(e))

    def exist(self, task_id):
        ret = self.__get_groupid(task_id)
        if ret:
            return True
        else:
            return False

    def __get_groupid(self, task_id):
        # 根据任务名称获取主机组id

        params = {
            "output": "groupid",
            "filter": {
                "name": [
                    task_id,
                ]
            }
        }
        groupids = self.zabbix.hostgroup.get(**params)
        if groupids:
            groupid = groupids[0]['groupid']
            return groupid

    def __create_hostgroup(self):
        """
        创建主机组并返回ID
        :return: string
        """
        res = self.zabbix.hostgroup.create(name=self.task_id)
        host_groupid = res['groupids'][0]
        return host_groupid

    def __create_template(self, groupid):
        """
        创建模版
        :param groupid: string 模版所属分组id
        :return:
        """
        params = {
            "host": self.task_id,  # 模版名称
            "templates": [{"templateid": self.base_template_id}],
            "groups": {
                "groupid": groupid
            }
        }

        res = self.zabbix.template.create(**params)
        template_id = res['templateids'][0]
        return template_id

    def __create_trigger(self, delay=None, loss=None):
        """
        添加触发器
        :param delay:float 延迟时间，单位s
        :param loss: int 丢包率 0-100
        :return: None
        """
        params = []
        if delay:
            # 延迟过高触发器参数
            delay_too_high = {
                "description": "ping delay too hign: {HOST.NAME}",
                "expression": "{%s:icmppingsec.last(,10)}>%s" % (self.task_id, delay),
                "priority": 3,
                "tags": [{"tag": "item", "value": '0'}]  # 设置标签，0：网络延迟
            }
            params.append(delay_too_high)

        if loss:
            # 丢包率过高触发器参数
            loss_too_high = {
                "description": "package loss rate too high: {HOST.NAME}",
                "expression": "{%s:icmppingloss.last(,10)}>%s" % (self.task_id, loss),
                "priority": 3,
                "tags": [{"tag": "item", "value": '1'}]  # 设置标签，1：丢包率
            }
            params.append(loss_too_high)

        res = self.zabbix.trigger.create(*params)

        return res["triggerids"]

    def __create_hosts(self, groupid, templateid, camera_list):
        """
        创建主机
        :param groupid:string
        :param templateid: string
        :param camera_list: dict
        :return:
        """
        params = []
        for uuid, ip in camera_list.items():
            host = {
                "host": "%s-%s" % (self.task_id, uuid),
                "interfaces": [
                    {
                        "type": 2,  # snmp
                        "main": 1,
                        "useip": 1,  # 使用ip
                        "ip": ip,
                        "dns": "",
                        "port": "161"
                    }
                ],
                "groups": [
                    {
                        "groupid": groupid
                    }
                ],
                "templates": [
                    {
                        "templateid": templateid
                    }
                ],
            }
            params.append(host)

        self.zabbix.host.create(*params)

    def __get_base_template_id(self, name="Patrol base template"):
        """
        获取基础模版的id，
        :param name: 模版名称，默认为 Patrol base template
        :return: 模版id
        """
        params = {
            "output": ["templateids"],
            "filter": {
                "name": [
                    name
                ]
            }
        }
        ret = self.zabbix.template.get(**params)
        if ret:
            return ret[0]['templateid']


def my_jsonrpc(zabbix, json_rpc):
    group, method = json_rpc['method'].split('.')
    # 反射
    group = getattr(zabbix, group)
    method = getattr(group, method)

    # if hasattr(dic, 'params'):
    params = json_rpc['params']
    if isinstance(params, dict):
        res = method(**params)
    elif isinstance(params, list):
        res = method(*params)
    else:
        res = method(params)

    print(res)


if __name__ == '__main__':
    # zabbix = ZabbixAPI("http://172.16.1.90/zabbix/")
    # zabbix.login("admin", "zabbix")
    # my_jsonrpc(zabbix, __create_trigger)
    helper = AssignZabbixTask()
    # 初始化
    helper.zabbix = ZabbixAPI("http://" + "172.16.101.71" + "/zabbix/")
    helper.zabbix.login("admin", "zabbix")
    helper.base_template_id = helper._AssignZabbixTask__get_base_template_id()

    cameras = {
        '1353707a1acc45579b744301e5700b30': "172.16.30.94",
        'c51d6891a14e4534a072161c80ba69f2': "172.16.30.245",
        'b60755f55144455f88df8a633d12cd1a': '45.76.76.198'
    }

    # helper.add('df7f94cc70a340eb8fbcb1603cc86393', delay=0.1, loss=5, camera_list=cameras)
    # helper.stop('df7f94cc70a340eb8fbcb1603cc86393')
    # helper.start('df7f94cc70a340eb8fbcb1603cc86393')
    # helper.delete('df7f94cc70a340eb8fbcb1603cc86393')
    res = helper.problem('953f3a9f70ae4254b86eb68ef2a47abc')
    print(res)
    # helper.get_base_template_id()
    # print(helper.exist('df7f94cc70a340eb8fbcb1603cc8693'))
    # zabbix_ip = self.app.config.get("ZABBIX_IP")
    # username = self.app.config.get('ZABBIX_USERNAME', "admin")
    # passwd = self.app.config.get('ZABBIX_PASSWD', "zabbix")
    from pyzabbix import ZabbixAPI
    zabbix = ZabbixAPI("http://" + "172.16.102.73:8080")
    zabbix.login("Admin", "zabbix")
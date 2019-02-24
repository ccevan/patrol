# 视频运维平台

> 实现对全网设备"全天候、全过程、全方位"集中监控
> 保证视频监控系统发挥最大效益

## 简介
视频运维平台适用于不同规模的视频监控系统的日常运维管理，系统对监控视频网络中前端、网络、存储、计算资源等全部设备运行信息进行采集，提供设备管理、设备及链路检测、视频质量诊断、网络拓扑可视化、巡检管理、告警提醒、工单管理、统计报表和绩效考核等日常运维管理应用功能，为视频监控系统发现故障、定位故障、跟踪处理情况及运维工作质量等提供全面支持。

### 视频质量诊断
对视频图像出现的雪花、滚屏、模糊、偏色、画面冻结、增益失衡、云台失控、视频信号丢失等常见摄像头故障、视频信号干扰、视频质量下降进行准确分析、判断和报警。

### 基础监控
底层采用zabbix，上层采用python对接zabbix jsonrpc webapi进行接口交互，基础监控功能如下：

 * 硬件监控
    - 通过SNMP、IPMI来进行路由器交换机的监控、服务器的温度等
 * 系统监控。
    - CPU的负载
    - 内存使用率
    - 磁盘读写
    - 磁盘使用率
    - 磁盘inode
 * 服务监控。
    - db：sqlserver、mysql、postgresql、oracle、redis、mongodb、Hadoop
    - 中间件：nginx、iis、tomcat、exchange、apache等
 * 网络监控
    - dns解析
    - 可用性
    - 网络速度
 * Web监控
    - js相应时间
    - 服务响应
 * 日志监控
    - 自定义日志
    - 服务日志

## Patrol(巡警) 接口
接口基于python语言3.x版本[flask-restful](http://www.pythondoc.com/Flask-RESTful/quickstart.html)框架开发。

> ### Auth 认证接口

>*  [Login](api_list#h21)  登录 
>*  [LoginOut](api_list#h21)  登出
>*  [Verify](api_list#h21)  验证码
  
> ### Org 组织结构

>*  [User API](api_list#h21)  用户
>*  [Organization](api_list#h22)  组织
>*  [Role](api_list#h22)  角色
    
> ### Asset 资产接口


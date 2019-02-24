[TOC]

# 用户角色接口

### 接口列表

#### 1. add Role

   description：创建角色

   * URL: /api/v1/role/addRole

   * Method：post

   * Header：Authorization=[string]

   * Url Params：

   * Data Params：

| 参数     | 必须 | 类型   | 说明   |
|--------|----|------|------|
| rolename | 是   | string | 角色名 |

   * Success Response：

     ```python
     {
         "code": 0,
         "message": "创建成功"
     }
     ```

   * Error Response：

     ```python
     {
         "code":-1,
         "message":"角色创建失败"
     }
     ```

   * Sample Call:

     ```python
     $.ajax({
         url:"http://host:port/api/v1/role/addRole",
         type:"post",
         async: false,
         contentType:"multipart/form-data",
         data : {"roleName":"name"},
         dataType:"json",
         success:function(data){
         # 请求成功处理
         },
         error:function(){
             # 请求出错处理
         }
     });
     ```

   * Note：

#### 2.  delete role by id

   description：通过用户Id删除角色

   * URL: /api/v1/role/deleteRoleById

   * Method： post

   * Header： Authorization=[string]

   * Url Params：

   * Data Params：

| 参数   | 必须 | 类型   | 说明   |
|------|----|------|------|
| userId | 是   | string | 用户id |

   * Success Response:

     ```python
     {
         "code":0,
         "message":"删除角色成功"
     }
     ```

   * Error Response:

     ```python
     {
         "code":-1,
         "message":"删除角色失败"
     }
     ```

   * Sample Call:

     ```python
     $.ajax({
         url:"http://host:port/api/v1/role/deleteRoleById",
         type:"post",
         async: false,
         contentType:"multipart/form-data",
         data : {
             "roleId":110,
             },
         dataType:"json",
         success:function(data){
         # 请求成功处理
         },
         error:function(){
             # 请求出错处理
         }
     });
     ```

   * Note:

#### 3.  update role by id

   description: 通过角色id更新角色信息

   * URL: /api/v1/role/updateRoleById

   * Method:post

   * Header:Authorization=[string]

   * Url Params:

   * Data Params:

| 参数     | 必须 | 类型   | 说明     |
|--------|----|------|--------|
| roleId   | 是   | int    | 角色ID   |
| roleName | 是   | string | 角色名称 |

   * Success Response:

     ```python
     {
         "code":0,
         "message":"更新角色成功"
     }
     ```

   * Error Response：

     ```python
     {
         "code":-1,
         "message":"更新角色失败"
     }
     ```

   * Sample Call:

     ```python
     $.ajax({
         url:"http://host:port/api/v1/role/updateRoleById",
         type:"post",
         async: false,
         contentType:"multipart/form-data",
         data : {
             "roleId":110,
             "roleName":"admin"
             },
         dataType:"json",
         success:function(data){
         # 请求成功处理
         },
         error:function(){
             # 请求出错处理
         }
     });
     ```

   * Note:

#### 4. get all roles 

   description： 获取所有角色信息

   - URL: /api/v1/role/getAllRoles

   - Method：get

   - Header: Authorization=[string]

   - Url Params:

   - Data Params:

   - Success Response:

     ```python
     {
         "code":0,
         "data":{
         [
             {
                 "roleId":"",
                 "roleName":""
             },
             {
                 "roleId":"",
                 "roleName":""
             }
         ]
             
         }，
         "message":"获取角色信息成功"
     }
     ```

   - Error Response:

     ```python
     {
         "code":-1,
         "message":"获取角色失败"
     }
     ```

   - Sample Call:

     ```python
     $.ajax({
         url:"http://host:port/api/v1/role/getAllRoles",
         type:"get",
         async: false,
         contentType:"multipart/form-data",
         dataType:"json",
         success:function(data){
         # 请求成功处理
         },
         error:function(){
             # 请求出错处理
         }
     });
     ```

   - Note:
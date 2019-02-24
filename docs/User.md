[TOC]

# User 用户接口

### 接口列表：

------

#### 1.  get all users

   description: 获取所有用户的信息

   * URL: /api/v1/user/getUsers

   * Method: get

   * Header: Authorization=[string]

   * Url Params:

   * Data Params:

   * Success Response

     ```python
     {
         "code":0,
         "data":{
         [
             {
                 "account":"",
                 "realname":"",
                 "phone"："",
                 "email":"",
                 "orgname":"",
             },
             {
                 "account":"",
                 "realname":"",
                 "phone"："",
                 "email":"",
                 "orgname":"",
             }
         ]

         }，
         "message":"获取用户信息成功"
     }
     ```

   * Error Response:

     ```python
     {
         "code":-1,
         "data":{
         [
             {
                 "account":"",
                 "realname":"",
                 "phone"："",
                 "email":"",
                 "orgname":"",
             },
             {
                 "account":"",
                 "realname":"",
                 "phone"："",
                 "email":"",
                 "orgname":"",
             }
         ]

         }，
         "message":"获取用户信息失败"
     }
     ```

   * Sample Call:

   * Notes:

#### 2.  delete user by id

   description: 通过用户id删除用户

   * URL：/api/v1/user/deleteUserById

   * Method：post

   * Header：Authorization=[string]

   * Url Params： 

   * Data Params：

| 参数   | 必须 | 类型   | 说明     |
|------|----|------|--------|
| userId | 是   | string | 用户的ID |

   * Success Response：

     ```python
     {
         "code":0,
         "message":"删除用户成功"
     }
     ```

   * Error Response：

     ```python
     {
         "code":-1,
         "message":"删除用户失败"
     }
     ```

   * Sample Call:

   * Note：

#### 3.   add user

   description: 添加用户

   * URL: /api/v1/user/addUser

   * Method：post

   * Header: Authorization=[string]

   * Url Params: 

   * Data Params:

| 参数     | 必须 | 类型   | 说明             |
|--------|----|------|----------------|
| account  | 是   | string | 用户账户名       |
| password | 是   | string | 用户密码         |
| realname | 否   | string | 用户真实姓名     |
| phone    | 否   | string | 用户电话号       |
| email    | 是   | string | 用户的邮箱       |
| orgid    | 否   | int    | 用户组织机构的id |

   * Error Response：

     ```python
     {
         "code":-1,
         "message":"添加用户失败"
     }
     ```

   * Sample Call:

     ```python
     $.ajax({  url:"http://host:port/api/v1/user/addUser",
         type:"post",
         async: false,
         contentType:"multipart/form-data",
         data : {
             "account":"a",
             "password":"123",
             "realname":"ing",
             "phone":"12345678901",
             "email":"123@qq.com",
             "orgid":110
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

#### 4. update the user infomation by id

   description: 修改用户信息

   * URL: /api/v1/user/updateUserById

   * Method：post

   * Header：Authorization=[string]

   * Url Params：

   * Data Params：

| 参数     | 必须 | 类型   | 说明             |
|--------|----|------|----------------|
| userId   | 是   | int    | 用户的ID         |
| account  | 否   | string | 用户的账户名     |
| password | 否   | string | 用户的密码       |
| realname | 否   | string | 用户的真实姓名   |
| phone    | 否   | string | 用户的电话号     |
| email    | 否   | string | 用户的邮箱       |
| orgId    | 否   | int    | 用户组织机构ID号 |
| image    | 否   | File   | 用户头像         |

   * Success Response：

     ```python
     {
         "code":0,
         "message":"更新用户信息成功"
     }
     ```

   * Error Response：

     ```python
     {
         "code":-1,
         "message":"更新用户信息失败"
     }
     ```

   * Sample Call:

     ```python
     $.ajax({
         url:"http://host:port/api/v1/user/updateUserById",
         type:"post",
         async: false,
         contentType:"multipart/form-data",
         data : {
             "userId":110,
             "account":"a",
             "password":"123",
             "realname":"ing",
             "phone":"12345678901",
             "email":"123@qq.com",
             "orgid":110,
             "image":<_io.file>
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

   * Note：

#### 5. update the user's password

   description：更改用户的密码

   * URL: /api/v1/user/updatePasswordById

   * Method: post

   * Header: Authorization=[string]

   * Url Params:

   * Data Params:

| 参数     | 必选 | 类型   | 说明           |
|--------|----|------|--------------|
| userid   | 是   | int    | 用户的id       |
| password | 是   | string | 用户的原始密码 |

   * Success Response：

     ```python
     {
         "code":0,
         "message":"更新用户密码成功"
     }
     ```

   * Error Response：

     ```python
     {
         "code":-1,
         "message":"更新用户密码失败"
     }
     ```

   * Sample Call:

     ```python
     $.ajax({
         url:"http://host:port/api/v1/user/updatePasswordById",
         type:"post",
         async: false,
         contentType:"multipart/form-data",
         data : {
             "userId":110,
             "oldpassword":"111"
             "newpassword":"123",
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

   * Note：

     ```python
     # 错误返回码
     {
         "code":-1,
         "message":"更新用户密码失败"
     }
     {
         "code":-2,
         "message":"更新用户密码失败"
     }
     ```



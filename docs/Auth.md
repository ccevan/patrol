# Auth 认证接口

## 认证方式

Auth认证采用JWT的方式。

### 接口列表

---

### 1、登录

description:

* URL: /api/v1/Auth/Login

* Header: Authorization=[String]

* Method: `POST`

* Data Params:

    |参数|必选|类型|说明|
    |:----- |:-----|:-----|----- |
    |account |ture |string|用户名|
    |password |true |string |密码|

* Success Response:

    ```json
        {
            "code": 0,
            "message": "登录成功",
            "user": {
                "userId": "[guid]",
                "account": "[string]",
                "realName": "[string]",
                "organizationName": "[string]",
                "departmentName": "[string]",
                "roleName": "[string]",
                "description": "[string]",
                "avatar": "[string]",
                "gender": "[bool]"
            }
        }
    ```

* Error Response:

    ```json
        {
        "code":-1,
        "message":"message content"
        }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/v1/Auth/Login",
        type:"post",
        async: false,
        contentType:"multipart/form-data",
        data : {"account":"a","password":"123"},
        dataType:"json",
        success:function(data){
        //请求成功处理
        },
        error:function(){
            //请求出错处理
        }
    });
    ```

* Notes:

### 2、登出

description:

* URL: /api/v1/Auth/Logout

* Header: Authorization=[String]

* Method: `GET`

* Success Response

    ```json
    {
        "code":0,
        "message":"注销成功"
    }
    ```

* Error Response

    ```json
    {
        "code":-1,
        "message":"注销失败"
    }
    ```

* Sample Call

    ```javascripy
    $.ajax({
        url:"http://host:port/api/v1/Auth/Logout",
        type:"get",
        async: false,
        headers: {
            "token":"[string]"
            },
            contentType:"multipart/form-data",
            dataType:"json",
            success:function(data){
                //请求成功处理
            },
            error:function(){
                //请求出错处理
            }
        });
    ```

* Note

### 3、忘记密码

* URL: /api/vi/Auth/ForgetPassword

* Header: Authorization=[String]

* Method: `POST`

* Data Params:

    |参数|必选|类型|说明|
    |:----- |:-------|:-----|----- |
    |account |ture |string|用户名|
    |phone |true |string |手机号|

* Success Response:

    ```json
    {
        "code":0,
        "message":"发送短信成功"
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"发送短信失败"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/v1/Auth/ForgetPassword",
        type:"post",
        async: false,
        contentType:"multipart/form-data",
        data : {"account":"a",email:"123@qq.com"},
        dataType:"json",
        success:function(data){
        //请求成功处理
        },
        error:function(){
            //请求出错处理
        }
    });

    ```

* Note

### 4、验证手机

* URL: /api/vi/Auth/validatePhone

* Header: Authorization=[String]

* Method: `POST`

* URL Params:

    |参数|必选|类型|描述|
    |:---|:---|:---|---|
    |account|true|string|用户名|
    |identifyCode|true|string|验证码|

* Success Response:

    ```json
    {
        "code":0,
        "message":"验证码正确"
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"验证码错误"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/vi/Auth/validatePhone",
        type:"post",
        async: false,
        contentType:"multipart/form-data",
        data : {"account":"a",
                identifyCode:"1230"},
        dataType:"json",
        success:function(data){
        //请求成功处理
        },
        error:function(){
            //请求出错处理
        }
    });
    ```

* Note

### 5、更新密码

* URL: /api/vi/Auth/updatePassword

* Header: Authorization=[String]

* Method: `POST`

* Data Params:

    |参数|必选|类型|描述|
    |:---|:---|:---|---|
    |account|是|string|用户名|
    |password|是|string|密码|

* Success Response:

    ```json
    {
        "code":0,
        "message":"更新密码成功"
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"更新密码失败"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/vi/Auth/updatePassword",
        type:"post",
        async: false,
        contentType:"multipart/form-data",
        data : {"account":"a", "password":"123456"},
        dataType:"json",
        success:function(data){
        //请求成功处理
        },
        error:function(){
            //请求出错处理
        }
    });
    ```

* Note:

### 6、生成验证码

* URL: /api/vi/Auth/getCAPTCHA

* Header: Authorization=[String]

* Method: `GET`

* Success Response:

    ```json
    {
        "code":0,
        "message":"获取验证码成功"
        "data":{
            "id":"[int]",
            "URL":"[string]"
        }
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"获取验证码失败"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/vi/Auth/CAPTCHA",
        type:"post",
        async: false,
        contentType:"multipart/form-data",
        data : {},
        dataType:"json",
        success:function(data){
        //请求成功处理
        },
        error:function(){
            //请求出错处理
        }
    });
    ```

#### 2、登出
---
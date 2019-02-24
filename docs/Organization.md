# 组织机构信息接口

## 接口列表

### 1、获取所有组织机构信息

* URL: /api/v1/Orgnization/getOrg

* Header: Authorization=[String]

* Method: `GET`

* Date Params:

    |参数|必选|类型|描述|
    |:---|:---|:---|---|

* Sccess Response

    ```json
    {
        "code":0,
        "message":"获取组织机构信息成功",
        "data":{
        [
            {
                "orgid":"[string]",
                "orgname":"[string]"
            }
        ]
        }
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"获取组织机构信息失败"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/vi/Orgnization/getOrg",
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

* Note:

### 2、添加组织机构

* URL: /api/v1/Orgnization/addOrg

* Header: Authorization=[String]

* Method: `POST`

* Date Params:

    |参数|必选|类型|描述|
    |:---|:---|:---|---|
    |orgname|是|string|组织机构名称|
    |description|否|string|组织机构描述|
    |parentid|否|string|父级机构id|

* Success Response

    ```json
    {
        "code":0,
        "message":"添加组织机构信息成功",
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"添加组织机构信息失败"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/vi/Orgnization/addOrg",
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

* Note:

### 3、更新组织机构

* URL: /api/v1/Orgnization/updateOrgById

* Header: Authorization=[String]

* Method: `POST`

* Date Params:

    |参数|必选|类型|描述|
    |:---|:---|:---|---|
    |orgid|是|string|组织机构id|
    |orgname|否|string|组织机构名称|
    |description|否|string|组织机构描述|
    |parentid|否|string|父级机构id|

* Success Response

    ```json
    {
        "code":0,
        "message":"更新组织机构信息成功",
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"更新组织机构信息失败"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/vi/Orgnization/updateOrgById",
        type:"post",
        async: false,
        contentType:"multipart/form-data",
        data : {"orgid":"3F2504E0-4F89-11D3-9A0C-0305E82C3301",
        "orgname":"二组"},
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

### 4、删除组织机构

* URL: /api/v1/Orgnization/deleteOrgById

* Header: Authorization=[String]

* Method: `POST`

* Date Params:

    |参数|必选|类型|描述|
    |:---|:---|:---|---|
    |orgid|是|string|组织机构id|

* Success Response

    ```json
    {
        "code":0,
        "message":"删除组织机构成功",
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"删除组织机构失败"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/vi/Orgnization/deleteOrgById",
        type:"post",
        async: false,
        contentType:"multipart/form-data",
        data : {"orgid":"3F2504E0-4F89-11D3-9A0C-0305E82C3301"},
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

### 5、给用户分配组织机构

* URL: /api/v1/Orgnization/AssignOrgById

* Header: Authorization=[String]

* Method: `POST`

* Date Params:

    |参数|必选|类型|描述|
    |:---|:---|:---|---|
    |orgid|是|string|组织机构id|
    |userid|是|string|人员id|

* Success Response

    ```json
    {
        "code":0,
        "message":"分配组织机构成功",
    }
    ```

* Error Response:

    ```json
    {
        "code":-1,
        "message":"分配组织机构失败"
    }
    ```

* Sample Call:

    ```javascript
    $.ajax({
        url:"http://host:port/api/vi/Orgnization/AssignOrgById",
        type:"post",
        async: false,
        contentType:"multipart/form-data",
        data : {"orgid":"3F2504E0-4F89-11D3-9A0C-0305E82C3301",
        "userid":"3F2504E0-4F89-11D3-9A0C-0305E82C3301"},
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

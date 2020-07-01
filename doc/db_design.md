# 数据库设计

使用`MongoDB`数据库

## 用户表

表名：user

```json
{
    "ObjectId" : "...",
    "account" : "String",	// 账号
    "password" : "String",	// 密码
    "name" : "String"		// 名称
}
```

## 项目表

表名：project

```json
{
    "ObjectId" : "...",
    "name" : "String",	// 项目名
    "createTime" : "Long", // 创建时间
    "creator" : "UserId",	// 创建者id
    "members" : [
        {
            "userId" : "String",	// 成员的ObjectId
            "permission" : "String" // 权限, r 或 w
        }
     ],
    "apis" : [	// 项目的api
        {
            "groupName" : "String", // 分组名称
            "apiIds" : [
                {
                    apiId
                }
            ]
        }
    ]
}
```

## 接口表

表名：api

```json
{
    "ObjectId" : "...",
    "name" : "String",	// 接口名称
    "protocol" : "Int", // 协议，0为http，1为https
    "url" : "String",	// 接口的url地址
    "group" : "String",	 // 接口的组名
    "status" : "Int",  // 接口的状态
    "explain" : "String",	  // 接口的说明信息
    "createTime" : "Long", // 接口的创建时间
    "createUser" : "UserId", // 接口的创建者
    "updateTime" : "Long",	 // 接口的最后更新时间
    "updateUser" : "UserId",	// 接口的最后更新人
    "requestMethod" : "Int",	// 请求方法
    "urlParam" : [
        {
            "paramKey" : "String",	// 参数名
            "paramExplain" : "String" // 参数说明 
        }
    ],
    "requestHeader" : [		// 请求头
        {
            "headerName" : "String", // 请求头名
            "headerValue" : "String", // 值
            "explain" : "String"	// 说明
        }
    ],
    "requestParamType" : "Int", // 请求参数类型
    "requestParamJsonType" : "Int", // 请求参数的JSON类型（Object还是Array）
    "requestParam" : [
       {
           "paramKey" : "String", //参数名
           "type" : "String", // 类型
           "explain" : "String",	// 说明
           "childList" : [
               requestParam
           ]
       } 
    ],	// 接口的请求参数
    "responseHeader" : [
        {
            "headerName" : "String", // 返回头名
            "headerValue" : "String", // 值
            "explain" : "String"	// 说明
        }
    ],
    "responseParam" : ReturnData		// 接口的返回数据
}
```
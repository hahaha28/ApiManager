

const base_url = "http://api.inaction.fun"
// const base_url = "http://127.0.0.1:9999"


/**
 * 发送get请求
 * @param url url不包括域名，以 / 开头
 * @param success 成功的返回
 */
function httpGET(url,success,err) {
    $.ajax({
        url: base_url+url,
        type: "GET",
        success: function (data,status,xhr) {
            success(xhr.responseJSON)
        },
        error: function (xhr, error, exception){
            err(xhr.status,xhr.responseJSON)
        }
    })
}

function httpPost(url,data,success,err){
    $.ajax({
        url: base_url+url,
        type: "POST",
        data: JSON.stringify(data),
        contentType: 'application/json',
        success: function (data,status,xhr) {
            success(xhr.responseJSON)
        },
        error: function (xhr, error, exception){
            console.log('test')
            err(xhr.status,xhr.responseJSON)
        }
    })
}


/**
 * 把时间戳转换为 x年x月x日 的字符串
 * @param timestamp 13位时间戳
 * @returns {string} x年x月x日
 */
function getYMD(timestamp) {
    var date = new Date(timestamp)
    const year = date.getFullYear();
    const month = date.getMonth();
    const day = date.getDate();
    return year+"年"+month+"月"+day+"日"
}

/**
 * 获取url参数
 * @type {{paramValues: UrlParam.paramValues, param: UrlParam.param, hasParam: (function(*): boolean), paramMap: (function(): {})}}
 */
UrlParam = function() { // url参数
    var data, index;
    (function init() {
        data = []; //值，如[["1","2"],["zhangsan"],["lisi"]]
        index = {}; //键:索引，如{a:0,b:1,c:2}
        var u = window.location.search.substr(1);
        if (u != '') {
            var params = decodeURIComponent(u).split('&');
            for (var i = 0, len = params.length; i < len; i++) {
                if (params[i] != '') {
                    var p = params[i].split("=");
                    if (p.length == 1 || (p.length == 2 && p[1] == '')) {// p | p= | =
                        data.push(['']);
                        index[p[0]] = data.length - 1;
                    } else if (typeof(p[0]) == 'undefined' || p[0] == '') { // =c 舍弃
                        continue;
                    } else if (typeof(index[p[0]]) == 'undefined') { // c=aaa
                        data.push([p[1]]);
                        index[p[0]] = data.length - 1;
                    } else {// c=aaa
                        data[index[p[0]]].push(p[1]);
                    }
                }
            }
        }
    })();
    return {
        // 获得参数,类似request.getParameter()
        param : function(o) { // o: 参数名或者参数次序
            try {
                return (typeof(o) == 'number' ? data[o][0] : data[index[o]][0]);
            } catch (e) {
            }
        },
        //获得参数组, 类似request.getParameterValues()
        paramValues : function(o) { // o: 参数名或者参数次序
            try {
                return (typeof(o) == 'number' ? data[o] : data[index[o]]);
            } catch (e) {}
        },
        //是否含有paramName参数
        hasParam : function(paramName) {
            return typeof(paramName) == 'string' ? typeof(index[paramName]) != 'undefined' : false;
        },
        // 获得参数Map ,类似request.getParameterMap()
        paramMap : function() {
            var map = {};
            try {
                for (var p in index) { map[p] = data[index[p]]; }
            } catch (e) {}
            return map;
        }
    }
}();


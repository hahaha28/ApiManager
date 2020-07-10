from flask import Blueprint, request, jsonify, session

from dbutil import db

api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/new/api', methods=['POST'])
def new_api():
    """
    新建接口

    :return:
    """
    # 检测参数是否合法
    check = check_new_api_param(request.json)
    if check[0] is False:
        return jsonify({'msg': check[1]}), 406
    # 检查项目id是否存在
    project_data = db.find_project(request.json['projectId'])
    if project_data is None:
        return jsonify({'msg': '项目id不存在'}, 406)
    # 检查用户是否是项目成员并拥有权限
    user_id = session['user_id']
    is_member = False
    permission = -1
    if project_data['creator'] == user_id:
        is_member = True
        permission = 1
    else:
        for member in project_data['members']:
            if member['userId'] == user_id:
                is_member = True
                permission = member['permission']
                break
    if is_member is False or permission != 1:
        return jsonify({'msg': 'no permission'}), 403
    # 参数合法则新建API
    api_id = db.create_api(user_id, request.json)
    api_id = str(api_id)
    # 将api添加到项目中
    db.add_project_api(request.json['projectId'], request.json['group'],
                       api_id, request.json['name'])
    return jsonify({'msg': 'ok', 'apiId': api_id}), 200


@api_bp.route('/delete/api', methods=['GET'])
def delete_api():
    api_id = request.args['id']
    # 先查找该api数据
    api_data = db.find_api(api_id)
    if api_data is None:
        return jsonify({'msg': 'api id not found'}), 404
    # 查找对应的项目数据
    project_data = db.find_project(api_data['projectId'])
    # 检测该用户是否是项目成员并有修改权限
    user_id = session['user_id']
    is_member = False
    permission = -1
    if project_data['creator'] == user_id:
        is_member = True
        permission = 1
    else:
        for member in project_data['members']:
            if member['userId'] == user_id:
                is_member = True
                permission = member['permission']
                break
    if is_member is False or permission != 1:
        return jsonify({'msg': 'no permission'}), 403
    # 删除api
    db.delete_api(api_id)
    db.delete_project_api(str(project_data['_id']), api_id)
    return jsonify({'msg': 'ok'}), 200


@api_bp.route('/find/api', methods=['GET'])
def find_api():
    """
    根据id查询api

    :return:
    """
    api_id = request.args['id']
    # 查找该api信息
    api_data = db.find_api(api_id)
    if api_data is None:
        return jsonify({"msg": "api id not found"}), 404
    # 查找该api所属的项目信息
    project_id = api_data['projectId']
    project_data = db.find_project(project_id)
    if project_data is None:
        return jsonify({"msg": "project not found"}), 404
    # 验证该用户是否是该项目成员
    is_member = False
    user_id = session['user_id']
    if project_data['creator'] == user_id:
        is_member = True
    else:
        for member in project_data['members']:
            if member['userId'] == user_id:
                is_member = True
                break
    if is_member is True:
        del api_data['_id']
        return jsonify(api_data), 200
    else:
        return jsonify({'msg': 'no permission'}), 407


def check_new_api_param(dict_data: dict) -> tuple:
    """
    检测新建接口的请求参数是否合法

    :param dict_data: 请求的参数，字典可是
    :return: 返回元组，第一个是是否成功，第二个是错误原因
    """
    # 首先检测字段是否都存在
    keys = ('projectId', 'name', 'protocol', 'url', 'group', 'status', 'explain', 'requestMethod',
            'urlParam', 'requestHeader', 'requestParamType', 'requestParamJsonType',
            'requestParam', 'requestRaw', 'requestExplain', 'responseData')
    check = check_param_key_exist(keys, dict_data)
    if check[0] is False:
        return check
    # 检测一些不能为空的值
    not_null_keys = ['name', 'protocol', 'url', 'group', 'status', 'requestMethod']
    for key in not_null_keys:
        if dict_data[key] is None:
            return False, f'{key}不能为null'
    # 检测数组对象的字段是否正确存在
    if len(dict_data['urlParam']) != 0:
        keys = ('paramKey', 'paramExplain')
        for urlParam in dict_data['urlParam']:
            check = check_param_key_exist(keys, urlParam)
            if check[0] is False:
                return check
    if len(dict_data['requestHeader']) != 0:
        keys = ('headerName', 'headerValue', 'explain')
        for requestHeader in dict_data['requestHeader']:
            check = check_param_key_exist(keys, requestHeader)
            if check[0] is False:
                return check
    if len(dict_data['requestParam']) != 0:
        keys = ('paramKey', 'type', 'explain', 'childList')
        for requestParam in dict_data['requestParam']:
            check = check_param_key_exist(keys, requestParam)
            if check[0] is False:
                return check
    if len(dict_data['responseData']) != 0:
        keys = ('responseHeader', 'responseParamType', 'responseParamJsonType',
                'responseParam', 'responseRaw', 'responseExplain')
        for responseData in dict_data['responseData']:
            check = check_param_key_exist(keys, responseData)
            if check[0] is False:
                return check
            if len(responseData['responseHeader']) != 0:
                keys1 = ('headerName', 'headerValue', 'explain')
                for responseHeader in responseData['responseHeader']:
                    check = check_param_key_exist(keys1, responseHeader)
                    if check[0] is False:
                        return check
            if len(responseData['responseParam']) != 0:
                keys2 = ('paramKey', 'type', 'explain', 'childList')
                for responseParam in responseData['responseParam']:
                    check = check_param_key_exist(keys2, responseParam)
                    if check[0] is False:
                        return check

    return True, "ok"


def check_param_key_exist(keys: tuple, data: dict) -> tuple:
    """
    检测字典data的key中是否存在keys中的数据

    :param keys: 需要存在的数据
    :param data: 待检测的字典
    :return: 元组第一个是True或False，第二个是字符串，错误的原因
    """
    for key in keys:
        if key not in data:
            return False, f'{key}不存在'
    return True, 'OK'

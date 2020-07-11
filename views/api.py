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
    if check_member_rw_permission(user_id, request.json['projectId']) is False:
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
    if check_member_rw_permission(user_id, api_data['project_id']) is False:
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
    is_member = check_member(session['user_id'], project_id)
    if is_member is True:
        del api_data['_id']
        return jsonify(api_data), 200
    else:
        return jsonify({'msg': 'no permission'}), 407


@api_bp.route('/update/api', methods=['POST'])
def update_api():
    """
    更新接口信息

    :return:
    """
    api_id = request.args['id']
    update_info = request.args['info']
    user_id = session['user_id']
    # 首先获取旧的api表的该api数据
    api_old_data = db.find_api(api_id)
    # 检测该用户是否是项目成员且有修改权限
    if check_member_rw_permission(user_id, api_old_data['projectId']) is False:
        return jsonify({'msg': 'no permission'}), 403
    # 将这条旧的数据保存到历史表中
    db.add_api_history(api_old_data)
    # 将新数据更改到api表中
    db.update_api(user_id, api_id, request.json, update_info)

    return jsonify({'msg': 'ok'}), 200


@api_bp.route('/find/api/history', methods=['GET'])
def find_api_history():
    """
    查找api的历史信息

    :return:
    """
    api_id = request.args['id']
    type = request.args['type']
    user_id = session['user_id']
    # 查找api的历史数据
    api_history_data = db.find_api_history(api_id)
    del api_history_data['_id']
    # 检测用户权限
    project_id = api_history_data['history'][0]['api']['projectId']
    if check_member(user_id,project_id) is False:
        return jsonify({'msg': 'no permission'}), 403
    # 根据type类型返回对应数据
    array_len = len(api_history_data['history'])
    if type == '1':
        # 处理ObjectId，因为这不是json类型
        for i in range(0,array_len):
            api_history_data['history'][i]['api']['_id'] = str(api_history_data['history'][i]['api']['_id'])
        return jsonify(api_history_data), 200
    elif type == '0':
        for i in range(0,array_len):
            del api_history_data['history'][i]['api']
        return jsonify(api_history_data), 200


def check_member(user_id: str, project_id: str) -> bool:
    """
    检查用户是否是项目成员

    :param user_id: 用户的id
    :param project_id: 项目的id
    :return: 如果是则返回True
    """
    is_member = False
    project_data = db.find_project(project_id)
    if project_data['creator'] == user_id:
        is_member = True
    else:
        for member in project_data['members']:
            if member['userId'] == user_id:
                is_member = True
                break
    return is_member


def check_member_rw_permission(user_id: str, project_id: str) -> bool:
    """
    检测用户是否是项目成员且有读写权限

    :param user_id: 用户的id
    :param project_id: 项目的id
    :return: 拥有权限则返回True
    """
    project_data = db.find_project(project_id)
    if project_data['creator'] == user_id:
        return True
    else:
        for member in project_data['members']:
            if member['userId'] == user_id:
                if member['permission'] == 1:
                    return True
                else:
                    return False
    return False


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

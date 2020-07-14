from flask import Blueprint, request, jsonify, session

from dbutil import db

user_bp = Blueprint('user_bp', __name__)


@user_bp.route('/register', methods=['POST'])
def register():
    """
    注册API

    :return:
    """
    data = request.json
    result = db.insert_user(
        data['account'],
        data['password'],
        data['name']
    )
    if result is True:
        return jsonify({
            'msg': 'ok'
        }), 200
    else:
        return jsonify({
            'msg': '账号已存在'
        }), 409


@user_bp.route('/update/user/data', methods=['POST'])
def update_user_data():
    """
    更新用户信息

    :return:
    """
    user_id = session['user_id']
    name = request.json['name']
    password = request.json['password']
    db.update_user(user_id,name,password)
    return jsonify({'msg': 'ok'}), 200


@user_bp.route('/login', methods=['POST'])
def login():
    """
    登录API

    :return:
    """
    request_param = request.json
    user = db.find_user(request_param['account'])
    # 先检查账号是否存在
    if user is None:
        return jsonify({
            'msg': '账号不存在'
        }), 404
    # 验证密码是否正确
    if user['password'] != request_param['password']:
        return jsonify({
            'msg': '密码错误'
        }), 409
    # 登录成功，在session中记录
    session['is_login'] = True
    session['user_id'] = str(user['_id'])
    return jsonify({
        'msg': 'ok'
    }), 200


@user_bp.route('/logout', methods=['GET'])
def log_out():
    """
    登出
    :return:
    """
    session['is_login'] = False
    del session['user_id']
    return jsonify({'msg': 'ok'}), 200


@user_bp.route('/user/data', methods=['GET'])
def get_user_data():
    """
    获取用户信息

    :return:
    """
    user_id = session['user_id']
    # 查询用户表
    user_data = db.find_user_by_id(user_id)
    # 查询用户创建的项目
    created_project = db.find_user_created_project(user_id)
    # 查询用户参加的项目
    joined_project = db.find_user_joined_project(user_id)
    # 构建返回数据
    project_data = []
    for i in created_project:
        members = []
        for member_data in i['members']:
            member_user_data = db.find_user_by_id(member_data['userId'])
            members.append({
                "account": member_user_data['account'],
                "name": member_user_data['name'],
                "permission": member_data['permission']
            })
        project_data.append({
            "id": str(i['_id']),
            "name": i['name'],
            "createTime": i['createTime'],
            "leaderAccount": user_data['account'],
            "leaderName": user_data['name'],
            "members": members
        })
    for i in joined_project:
        leader_data = db.find_user_by_id(i['creator'])
        members = []
        for member_data in i['members']:
            member_user_data = db.find_user_by_id(member_data['userId'])
            members.append({
                "account": member_user_data['account'],
                "name": member_user_data['name'],
                "permission": member_data['permission']
            })
        project_data.append({
            "id": str(i['_id']),
            "name": i['name'],
            "createTime": i['createTime'],
            "leaderAccount": leader_data['account'],
            "leaderName": leader_data['name'],
            "members": members
        })

    result = {
        "name": user_data['name'],
        "account": user_data['account'],
        "password": user_data['password'],
        "project": project_data
    }
    return jsonify(result), 200
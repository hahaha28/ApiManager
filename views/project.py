
from flask import Blueprint, request, jsonify, session

from dbutil import db

project_bp = Blueprint('project_bp',__name__)


@project_bp.route('/new/project', methods=['POST'])
def new_project():
    """
    新建项目

    :return:
    """
    request_data = request.json
    # 首先检查成员账号是否存在
    members = []
    not_found_members = []
    for member in request_data['members']:
        user_data = db.find_user(member['account'])
        if user_data is None:
            not_found_members.append(member['account'])
        else:
            members.append({
                "userId": str(user_data['_id']),
                "permission": member['permission']
            })
    # 数据库添加项目信息
    creator = session['user_id']
    project_id = db.create_project(creator, request_data['name'], members)
    project_id = str(project_id)
    # 如果有不存在的账号，返回404
    if len(not_found_members) != 0:
        return jsonify({
            "projectId": project_id,
            "notFound": not_found_members
        }), 404
    # 正常返回200
    return jsonify({
        "projectId": project_id
    })


@project_bp.route('/find/project/apis', methods=['GET'])
def find_project_apis():
    """
    获取项目的api信息

    :return:
    """
    project_id = request.args['id']
    project_data = db.find_project(project_id)
    if project_data is None:
        return jsonify({'msg':'id not found'}),404
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
        return jsonify(project_data['apis']), 200
    else:
        return jsonify({'msg': 'no permission'}), 407


@project_bp.route('/new/project_member', methods=['POST'])
def new_project_member():
    """
    添加项目成员

    :return:
    """
    request_data = request.json
    # 首先查找项目是否存在
    project_data = db.find_project(request_data['projectId'])
    if project_data is None:
        return jsonify({"msg": "用户账号或项目不存在"}), 404
    # 再检查用户账号是否存在
    user_data = db.find_user(request_data['account'])
    if user_data is None:
        return jsonify({"msg": "用户账号或项目不存在"}), 404
    # 检查账号是否已在项目成员中
    user_id = str(user_data['_id'])
    if user_id == project_data['creator']:
        return jsonify({"msg": "不能重复加入"})
    for member in project_data['members']:
        if user_id == member['userId']:
            return jsonify({"msg": "不能重复加入"})
    # 添加数据
    db.add_project_member(
        request_data['projectId'],
        str(user_id),
        request_data['permission']
    )
    return jsonify({"msg": "ok"}), 200


@project_bp.route('/update/member/permission', methods=['POST'])
def update_member_permission():
    """
    修改项目成员权限

    :return:
    """
    project_id = request.json['projectId']
    account = request.json['account']
    # 检查项目id合法性
    project_data = db.find_project(project_id)
    if project_data is None:
        return jsonify({"msg": "client error"}), 405
    # 检查发起修改者是否是项目组长
    if session['user_id'] != project_data['creator']:
        return jsonify({"msg": "client error"}), 405
    # 检查用户账号合法性
    user_data = db.find_user(account)
    if user_data is None:
        return jsonify({"msg": "client error"}), 405
    user_id = str(user_data['_id'])
    # 检查该用户是否属于该项目
    is_member = False
    for member in project_data['members']:
        if user_id == member['userId']:
            is_member = True
    if is_member == False:
        return jsonify({"msg": "client error"}), 405
    # 数据都合法，开始进行修改
    db.update_member_permission(
        project_id,
        user_id,
        request.json['permission']
    )
    return jsonify({"msg": "ok"}), 200


@project_bp.route('/delete/member', methods=['POST'])
def delete_member():
    """
    删除项目成员

    :return:
    """
    pass
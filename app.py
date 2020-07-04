from flask import Flask, render_template, request, jsonify, session, redirect
from dbutil import DBUtil

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = 'askdfwef1k2j31ga'
db = DBUtil()


@app.before_request
def before_request():
    # 检测登录状态，如果没登录则跳转到登录页面
    should_login = True
    path = request.path
    print(path)
    if 'bootstrap-4.5.0-dist' in path:
        # 访问bootstrap资源不需要登录
        should_login = False
    elif 'jquery-3.5.1.min.js' in path:
        # 访问jquery资源不需要登录
        should_login = False
    elif path == '/' or path == '/register':
        # 访问登录和注册页面不需要登录
        should_login = False
    elif path == '/static/ApiManagerFront/html/login.html' or \
            path == '/static/ApiManagerFront/html/register.html':
        # 访问登录和注册的静态页面不需要登录
        should_login = False
    if should_login == True:
        return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/static/ApiManagerFront/html/login.html')


@app.route('/register', methods=['POST'])
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


@app.route('/login', methods=['POST'])
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


@app.route('/new/project', methods=['POST'])
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


@app.route('/new/project_member', methods=['POST'])
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


@app.route('/update/member/permission', methods=['POST'])
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


@app.route('/delete/member', methods=['POST'])
def delete_member():
    """
    删除项目成员

    :return:
    """
    pass


@app.route('/user/data', methods=['GET'])
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
            "leaderAccount": leader_data['account'],
            "leaderName": leader_data['name'],
            "members": members
        })

    result = {
        "name": user_data['name'],
        "account": user_data['account'],
        "project": project_data
    }
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)

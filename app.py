from flask import Flask, render_template, request, jsonify, session, redirect
from dbutil import DBUtil

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = 'askdfwef1k2j31ga'
db = DBUtil()


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)

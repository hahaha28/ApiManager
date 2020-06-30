from flask import Flask, render_template, request, jsonify, session
from dbutil import DBUtil

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.secret_key = 'askdfwef1k2j31ga'
db = DBUtil()


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('helloworld.html')


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
    session['account'] = request_param['account']
    return jsonify({
        'msg': 'ok'
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)

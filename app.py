from flask import Flask, render_template, request, jsonify, session, redirect
from dbutil import db
from views.user import user_bp
from views.project import project_bp
from views.api import api_bp

app = Flask(__name__)
app.register_blueprint(user_bp)
app.register_blueprint(project_bp)
app.register_blueprint(api_bp)

app.config['JSON_AS_ASCII'] = False
app.secret_key = 'askdfwef1k2j31ga'


@app.before_request
def before_request():
    # 检测登录状态，如果没登录则跳转到登录页面
    should_login = True
    path = request.path
    if 'is_login' in session and session['is_login'] is True:
        # 已登录不需要再登陆
        should_login = False
    elif 'bootstrap-4.5.0-dist' in path:
        # 访问bootstrap资源不需要登录
        should_login = False
    elif 'jquery-3.5.1.min.js' in path:
        # 访问jquery资源不需要登录
        should_login = False
    elif path == '/' or path == '/register' or path == '/login':
        # 访问登录和注册页面不需要登录
        should_login = False
    elif path == '/static/ApiManagerFront/html/login.html' or \
            path == '/static/ApiManagerFront/html/register.html':
        # 访问登录和注册的静态页面不需要登录
        should_login = False
    if should_login is True:
        print(f'访问{path}，重定向')
        return redirect('/')


@app.route('/', methods=['GET', 'POST'])
def index():
    return redirect('/static/ApiManagerFront/html/login.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)

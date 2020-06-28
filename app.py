from flask import Flask, render_template

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False


@app.route('/',methods=['GET','POST'])
def index():
    return render_template('helloworld.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
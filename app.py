from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import create_access_token, JWTManager, jwt_required

from utils import db_util


app = Flask(__name__)
jwt = JWTManager()
CORS(app)
app.config['JWT_SECRET_KEY'] = 'temp_secrete_key'
jwt.init_app(app)

@app.route('/login', methods=['POST'])
def login():
    operator = db_util.DbOperator()
    username = request.json['username']
    password = request.json['password']
    if operator.login_check(username, password):
        access_token = create_access_token(identity=username)
        return jsonify(msg="Login passed", access_token=access_token)
    else:
        return jsonify(msg="Invalid password"), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0')
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from login import db_util

loginApp = Blueprint('loginBp', __name__)


@loginApp.route('/login', methods=['POST'])
def login():
    operator = db_util.DbOperator()
    username = request.json['username']
    password = request.json['password']
    print('username: ', username, '\n', 'password: ', password)
    if operator.login_check(username, password):
        print('check')
        access_token = create_access_token(identity=username)
        return jsonify({'verification': "Login passed", 'access_token': access_token})
    else:
        print(jsonify({'verification': "Invalid password", 'access_token': None}))
        return jsonify({'verification': "Invalid password", 'access_token': None})

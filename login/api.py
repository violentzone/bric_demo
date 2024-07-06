from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from login import db_util

loginApp = Blueprint('loginBp', __name__)
operator = db_util.DbOperator()


@loginApp.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    if operator.login_check(username, password):
        access_token = create_access_token(identity=username)
        userID, username_rsp = operator.user_info(username)
        return jsonify({'verification': "Login passed", 'access_token': access_token, 'userID': userID, 'username': username_rsp})
    else:
        return jsonify({'verification': "Invalid password", 'access_token': None, 'userID': None, 'username': None})


@loginApp.route('/create_user', methods=['POST'])
@jwt_required()
def create_user():
    user_id = request.json['user_id']
    name = request.json['name']
    identification = request.json['identification']
    department = request.json['department']
    supervisor1 = request.json['supervisor1']
    supervisor2 = request.json['supervisor2']
    supervisor3 = request.json['supervisor3']
    substitute = request.json['substitute']
    username = request.json['username']
    password = request.json['password']
    response = {'status': 'init', 'user_id': None}

    try:
        response_op = operator.create_user(user_id, username, password, substitute, name, identification, supervisor1, supervisor2, supervisor3, department)
        if response_op:
            response = {'status': 'succeed', 'user_id': user_id}
        else:
            response = {'status': 'ID_used', 'user_id': None}
    except:
        response = {'status': 'failed', 'user_id': None}

    finally:
        return response


@loginApp.route('/login_check', methods=['POST'])
@jwt_required()
def login_check():
    user_id = request.json['user_id']
    user_check = operator.check_user(user_id)

    if user_check:
        if user_id == '1':
            return jsonify({'user': 'admin'})
        else:
            return jsonify({'user': 'member'})
    else:
        return jsonify({'user': None})

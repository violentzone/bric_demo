from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required
from login import db_util

loginApp = Blueprint('loginBp', __name__)
operator = db_util.DbOperator()


@loginApp.route('/login', methods=['POST'])
def login():
    operator.logon_check()
    username = request.json['username']
    password = request.json['password']
    if operator.login_check(username, password):
        access_token = create_access_token(identity=username)
        userID, username_rsp = operator.user_info(username)
        return jsonify({'verification': "Login passed", 'access_token': access_token, 'userID': userID, 'username': username_rsp})
    else:
        return jsonify({'verification': "Invalid password", 'access_token': None, 'userID': None, 'username': None})


@loginApp.route('/create', methods=['POST'])
def create_user():
    try:
        # TODO: Not finished
        return True
    except:
        return False

@loginApp.route('/login_check', methods=['POST'])
@jwt_required()
def login_check():
    user_id = request.json['user_id']
    # TODO: Check if userID in db
    if user_id == 0:
        return jsonify({'user': 'admin'})


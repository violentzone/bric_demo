from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from login import db_util

loginApp = Blueprint('loginBp', __name__)
operator = db_util.DbOperator()

@loginApp.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    if operator.login_check(username, password):
        access_token = create_access_token(identity=username)
        return jsonify({'verification': "Login passed", 'access_token': access_token})
    else:
        return jsonify({'verification': "Invalid password", 'access_token': None})

@loginApp.route('/create', methods=['POST'])
def create_user():
    try:
        username_create = request.json['username']
        password_create = request.json['password']
        operator.create_user(username_create, password_create)
        return True
    except:
        return False
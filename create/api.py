from flask import Blueprint, request, jsonify
from create import db_util

createApp = Blueprint('createBp', __name__)
operator = db_util.DbOperator()


@createApp.route('/creator_info', methods=['POST'])
def creator_info():
    userid = request.json['user_id']
    user_info = operator.create_leave_getinfo(userid)
    return jsonify(user_info)


@createApp.route('/creator_create', methods=['POST'])
def creator_create():
    creator_id = request.json['user_id']
    substitute = request.json['substitute']
    start_time = request.json['start_time']
    end_time = request.json['end_time']
    leave_type_idx = request.json['leave_type_idx']
    reason = request.json['reason']
    print(request.json)



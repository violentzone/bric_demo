from flask import Blueprint, request, jsonify
from create import db_util
from flask_jwt_extended import jwt_required

createApp = Blueprint('createBp', __name__)
operator = db_util.DbOperator()


@createApp.route('/creator_info', methods=['POST'])
@jwt_required()
def creator_info():
    userid = request.json['user_id']
    user_info = operator.create_leave_getinfo(userid)
    return jsonify(user_info)


@createApp.route('/creator_submit', methods=['POST'])
@jwt_required()
def creator_create():
    creator_id = request.json['user_id']
    substitute = request.json['substitute']
    start_time = (request.json['start_time'])
    end_time = request.json['end_time']
    leave_type_idx = int(request.json['leave_type_idx'])
    reason = request.json['reason']
    response = operator.create_apply(creator_id, substitute, start_time, end_time, leave_type_idx, reason)
    return jsonify(response)

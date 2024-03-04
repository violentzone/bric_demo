from flask import Blueprint, request, jsonify
from create import db_util

createApp = Blueprint('createBp', __name__)
operator = db_util.DbOperator()


@createApp.route('/creator_info', methods=['POST'])
def creator_info():
    userid = request.json['user_id']
    user_info = operator.create_leave_getinfo(userid)
    return user_info

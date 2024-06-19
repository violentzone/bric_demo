from flask import request, Blueprint, jsonify
from annualLeaveSummary.db_util import DbOperator

annual_leave_summaryApp = Blueprint('annualLeaveBp', __name__)
operator = DbOperator()


@annual_leave_summaryApp.route('/annual_leave_summary', methods=['POST'])
def get_full_data():
    user_id = request.json['user_id']
    given, expire = operator.get_init_expire(user_id)
    data = operator.get_frame_data(user_id)
    name = operator.get_user_name(user_id)
    full_data = {'given': given, 'expire': expire, 'data': data, 'name': name}
    return jsonify(full_data)


@annual_leave_summaryApp.route('/overtime_leave_detail', methods=['POST'])
def get_all_data():
    user_id = request.json['user_id']
    data = operator.get_overtime_detail(user_id)
    total = operator.get_overtime_total(user_id)
    remains = operator.get_overtime_remain(user_id)
    name = operator.get_user_name(user_id)
    full_data = {'data': data, 'total': total, 'remains': remains, 'name': name}
    return jsonify(full_data)

from flask import Blueprint, request, jsonify
from check.db_util import DbOperator
from global_util.global_util import get_user_info

checkApp = Blueprint('checkBP', __name__)
operator = DbOperator()

@checkApp.route('/get_check', methods=["POST"])
def get_check():
    """
    Pass in user ID and gets information needed for check webpage
    {
    user:
    top :{
        last_year_inherit:
        this_year_total:
        last_year_expire:
        this_year_expire:
        used_leave:
        overtime_total:
        overtime_used:
        overtime_overdue:
        overtime_remain:
        },
     bottom: [
        {
        leave_type:
        leave_start:
        leave_end:
        duration:
        }, ...
        ]}
    """
    user_id = request.json['user_id']
    # Getting all information
    last_year_inherit = operator.get_last_year_annual_leave(user_id)
    this_year_total = operator.get_current_year_annual_leave(user_id)
    last_year_expire = operator.get_last_year_expire(user_id)
    this_year_expire = operator.get_current_year_expire(user_id)
    used_leave = operator.get_used_leave(user_id)
    overtime_total = operator.get_overtime_total(user_id)
    overtime_used = operator.get_over_time_used(user_id)
    overtime_overdue = operator.get_overtime_overdue(user_id)
    overtime_remain = operator.get_overtime_remain(user_id)
    user_name = operator.get_user_name(user_id)

    return jsonify({'top': {'last_year_inherit': last_year_inherit,
                            'this_year_total': this_year_total,
                            'last_year_expire': last_year_expire,
                            'this_year_expire': this_year_expire,
                            'used_leave': used_leave,
                            'overtime_total': overtime_total,
                            'overtime_used': overtime_used,
                            'overtime_overdue': overtime_overdue,
                            'overtime_remain': overtime_remain},
                    'bottom': operator.get_recent_used(user_id),
                    'user_name': user_name})

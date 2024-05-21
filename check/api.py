from flask import Blueprint, request, jsonify
from check.db_util import DbOperator

checkApp = Blueprint('checkBP', __name__)
operator = DbOperator()


@checkApp.route('/get_check', methods=["POST"])
def get_check():
    """
    Pass in user ID and gets information needed for check webpage
    {top :{
        last_year_inherit:
        this_year_total:
        last_year_expire:
        this_year_expire:
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




from flask import request, Blueprint
from annualLeaveSummary.db_util import DbOperator

annual_leave_summaryApp = Blueprint('annualLeaveBp', __name__)
operator = DbOperator()


@annual_leave_summaryApp.route('/annual_leave_summary', methods=['POST'])
def get_full_data():
    user_id = request.json['user_id']
    given, expire = operator.get_init_expire(user_id)
    print('api', given, expire)
    return {}

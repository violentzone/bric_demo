from flask import request, Blueprint
from annualLeaveSummary.db_util import DbOperator

annual_leave_summaryApp = Blueprint('annualLeaveBp', __name__)
operator = DbOperator()


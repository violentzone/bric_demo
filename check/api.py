from flask import Blueprint, request, jsonify


checkApp = Blueprint('checkBP', __name__)


@checkApp.route('/get_check', methods=["POST"])
def get_check():
    """
    Pass in user ID and gets information needed for check webpage
    {
    last_year_inherit:
    this_year_total:
    last_year_deadline:
    this_year_deadline:
    overtime_total:
    overtime_used:
    overtime_overdue:
    overtime_remain:
    }
    """
    pass

@checkApp.route('/get_recent', methods=['POST'])
def get_recent():
    """
    Pass in user ID and gets the user's recent(3) leave application
    [
    {
    leave_type:
    leave_start:
    leave_end:
    duration:
    }, ...
    ]
    """
    pass

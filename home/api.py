from flask import Blueprint, request, jsonify
from home import db_util

homeApp = Blueprint('homeBp', __name__)

@homeApp.route('/formscount')
def formscount():
    userid = request.json['user_id']
    homedb = db_util.DbOperator()
    form_count = homedb.unsign_num(userid)
    return jsonify({'form_count': form_count})
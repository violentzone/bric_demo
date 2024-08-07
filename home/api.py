from flask import Blueprint, request, jsonify
from home import db_util
from flask_jwt_extended import jwt_required

homeApp = Blueprint('homeBp', __name__)
operator = db_util.DbOperator()


@homeApp.route('/formscount', methods=['POST'])
@jwt_required()
def formscount():
    userid = request.json['user_id']
    form_count = operator.unsign_num(userid)
    name = operator.id_to_name(userid)
    return jsonify({'form_count': form_count, 'name': name})


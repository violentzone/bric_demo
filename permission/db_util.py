import pymysql
from json import loads

class DbOperator:
    def __init__(self):
        with open('infos/db.json') as f:
            db_config = loads(f.read())
        connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'], database=db_config['database'])

        # Create permission table if not exists
        check_permission_sql = """
        SELECT TABLE_NAME FROM information_schema.tables
        WHERE TABLE_SCHEMA = 'leavesystem'
        AND TABLE_NAME = 'permission'
        """

        with connection.cursor() as cursor:
            cursor.execute(check_permission_sql)
            permission_check = cursor.fetchone()

        if permission_check is None:
            pass
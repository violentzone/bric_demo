import pymysql
from json import loads

class DbOperator:
    def __init__(self):
        """
        Create sign table if not exists
        """
        with open('infos/db.json') as f:
            db_config = loads(f.read())
        connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'], database=db_config['database'])
        check_sign = """
                SELECT TABLE_NAME FROM information_schema.tables
                WHERE TABLE_SCHEMA = 'leavesystem'
                AND TABLE_NAME = 'sign'
                """
        cursor = connection.cursor()
        cursor.execute(check_sign)
        sign_check = cursor.fetchone()

        if sign_check is None:
            create_sign_sql = '''
            CREATE TABLE IF NOT EXISTS leavesystem.sign(
            ID varchar(255) NOT NULL,
            userID BIGINT NOT NULL,
            substituteID BIGINT,
            start_time datetime,
            end_time datetime,
            duration float,
            leave_type int,
            reason text,
            PRIMARY KEY (ID)
            )
            '''
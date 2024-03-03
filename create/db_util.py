import pymysql
from json import loads
from datetime import datetime

class DbOperator:
    def __init__(self):
        """
        Create leavesystem.create table if not exists
        """
        # Read setting
        with open('infos/db.json') as f:
            db_config = loads(f.read())
        connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'], database=db_config['database'])

        # Check create table syntext of MySQL
        check_create = """
        SELECT TABLE_NAME FROM information_schema.tables
        WHERE TABLE_SCHEMA = 'leavesystem'
        AND TABLE_NAME = 'create'
        """
        cursor = connection.cursor()
        cursor.execute(check_create)
        create_check = cursor.fetchone()

        if create_check is None:
            create_create_sql = """
            CREATE TABLE IF NOT EXISTS leavesystem.create(
            ID varchar(255) NOT NULL,
            userID BIGINT NOT NULL,
            substituteID BIGINT,
            start_time datetime,
            end_time datetime,
            leave_type int,
            reason text,
            PRIMARY KEY (ID)
            )
            """
            cursor.execute(create_create_sql)
            connection.commit()

        # Check leavetype table syntext of MySQL
        check_leave_type = """
        SELECT TABLE_NAME FROM information_schema.tables
        WHERE TABLE_SCHEMA = 'leavesystem'
        AND TABLE_NAME = 'leavetype'
        """
        cursor.execute(check_leave_type)
        leavetype_check = cursor.fetchone()

        if leavetype_check is None:
            create_leavetype_sql = """
            CREATE TABLE IF NOT EXISTS leavesystem.leavetype(
            ID INT NOT NULL AUTO_INCREMENT,
            chinese text NOT NULL,
            english text,
            PRIMARY KEY (ID)
            ) AUTO_INCREMENT = 1
            """
            cursor.execute(create_leavetype_sql)
            connection.commit()

        # Check leaveleft table syntext of MySQL
        check_leave_left = """
        SELECT TABLE_NAME FROM information_schema.tables
        WHERE TABLE_SCHEMA = 'leavesystem'
        AND TABLE_NAME = 'leaveleft'
        """
        cursor.execute(check_leave_left)
        leaveleft_check = cursor.fetchone()

        if leaveleft_check is None:
            create_leaveleft_sql = """
            CREATE TABLE IF NOT EXISTS leavesystem.leaveleft(
            userID, BIGINT NOT NULL,
            leave_type INT,
            hours float,
            expire datetime
            )
            """
            cursor.execute(create_leaveleft_sql)
            connection.commit()

        cursor.close()
        self.connection = connection

    def create_leave_getinfo(self, user_id: int):
        # with self.connection.cursor() as cursor:


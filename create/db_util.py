import pymysql
from json import loads
from datetime import datetime
from home import db_util as home_db
from uuid import uuid4

from create import util


class DbOperator:
    def __init__(self):
        """
        Create leavesystem.create, leavesystem.leavetype and leavesystem.leaveleft table if not exists
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
            duration float,
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
            basic_leaves_sql = """
            INSERT  INTO leavesystem.leavetype (chinese, english)
            VALUES 
            ('特休', 'Annual leave'), 
            ('事假', 'Personal leave'), 
            ('病假', 'Sick leave'), 
            ('公假', 'Official leave'),
            ('生理假', 'Menstruation leave'), 
            ('婚假', 'Marriage leave'), 
            ('產假', 'Maternity leave'),
            ('陪產假', 'Paternity leave'),
            ('喪假', 'Funeral leave'),
            ('無薪假', 'Unpaid leave'),
            ('帶薪休假', 'Paid leave')
            """
            cursor.execute(create_leavetype_sql)
            cursor.execute(basic_leaves_sql)
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
            CREATE TABLE IF NOT EXISTS leavesystem.leaveleft (
            userID BIGINT NOT NULL,
            leave_type INT,
            hours float,
            expire datetime
            )
            """
            cursor.execute(create_leaveleft_sql)
            connection.commit()

        cursor.close()
        self.connection = connection


    def create_leave_getinfo(self, user_id: int) -> dict:
        """
        Input userID return user inforamtion

        Params
        =======
        user_id: userID

        Return
        =======
        Dict of {'user_id':  'name':  'supervisorID_1':, 'suervisorName_1', 'supervisorID_2':, 'suervisorName_2', 'supervisorID_3': ,'suervisorName_3', 'department': , 'level': , 'leave_remain'DICT/ 'error'(str)}
        """
        # Get set leave
        get_leave_type_sql = """
        SELECT * FROM leavesystem.leavetype
        """
        with self.connection.cursor() as cursor:
            cursor.execute(get_leave_type_sql)
            leave_query = cursor.fetchall()
        leave_type_dict = {leave_set[0]: leave_set[1] + leave_set[2] for leave_set in leave_query}

        # Get apply user information
        with self.connection.cursor() as cursor:
            create_user_sql = """
            SELECT ID, name, supervisorID_1, supervisorID_2, supervisorID_3, department, level
            FROM leavesystem.users
            WHERE ID = %s
            """
            cursor.execute(create_user_sql, user_id)
            user_info = cursor.fetchone()

        # Get supervisor's name, if supervisor 1 is None, then don't need to keep checking supervisor 2 as well
        supervisorID_list = list((user_info[2:5]))

        supervisor_name_sql = """
        SELECT name FROM leavesystem.users WHERE ID = %s
        """
        for i in range(len(supervisorID_list)):
            if supervisorID_list[i] is None:
                break
            else:
                with self.connection.cursor() as cursor:
                    cursor.execute(supervisor_name_sql, supervisorID_list[i])
                    supervisorID_list[i] = str(supervisorID_list[i]) + '    ' + cursor.fetchone()[0]

        # Get user remain leaves -> get leave type dict, find the key(leaveID), build element leave_remain dict of the minus applying leave respectively
        with self.connection.cursor() as cursor:
            # Remain leaves
            get_leave_sql = """ 
            SELECT leave_type, hours FROM leavesystem.leaveleft
            WHERE userID = %s
            """
            # Applying leaves
            get_apply_sql = """
            SELECT leave_type, duration FROM leavesystem.create
            WHERE userID = %s
            """
            cursor.execute(get_leave_sql, user_id)
            leave_remain = cursor.fetchall()
            cursor.execute(get_apply_sql, user_id)
            creating_list = cursor.fetchall()
        leave_remain_dict = {leave[0]: leave[1] for leave in leave_remain}
        creating_dict = {creating[0]: creating[1] for creating in creating_list}
        dict_diff = util.leave_dict_diff(leave_remain_dict, creating_dict)
        if dict_diff['status'] == 'valid':
            leave_remain_return = dict_diff['content']
            return {'user_id':user_info[0], 'name': user_info[1], 'supervisor1': supervisorID_list[0], 'supervisor2': supervisorID_list[1], 'supervisor3': supervisorID_list[2], 'department': user_info[5], 'level': user_info[6], 'leave_remain': leave_remain_return}
        else:
            error_message = dict_diff['content']
            return {'user_id':user_info[0], 'name': user_info[1], 'supervisor1': supervisorID_list[0], 'supervisor2': supervisorID_list[1], 'supervisor3': supervisorID_list[2], 'department': user_info[5], 'level': user_info[6], 'error': error_message}


    def create_apply(self, user_id: int, start_time: datetime, end_time: datetime, leave_type: int, reason: str) -> dict:
        """
        Function after user send out leave application

        Params
        =======
        userID(int): Applicant's ID.
        start_time(datatime): Leave start time.
        end_time(datatime): Leave end time.
        leave_type(int): The leave type of the application.
        reason(str): Recorded leave reason.

        Return
        =======
        If succeed:
        {'result': 'success', 'message': None}
        If failed:
        {'result': 'fail', 'message': 'the_reason'}
        """

        # Check used leave and leave under apply

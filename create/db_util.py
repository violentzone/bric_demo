import pymysql
from json import loads
from datetime import datetime
from global_util import global_util
from uuid import uuid4
from global_util.connection_pool import POOL


from create import util


class DbOperator:
    def __init__(self):
        """
        Create leavesystem.create, leavesystem.leavetype and leavesystem.leaveleft table if not exists
        """
        connection = POOL.connection()

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
            ('帶薪休假', 'Paid leave'),
            ('補休', 'Overtime leave')
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
            expire datetime, 
            inherited int
            )
            """
            cursor.execute(create_leaveleft_sql)
            connection.commit()

        cursor.close()
        self.connection = connection

    def get_leave_left(self, user_id: int, leave_type_idx) -> dict:
        """
        Get current leave left of a user

        Params
        =======
        user_id: The user id to check from

        Return
        =======
        Dict of each leave left
        """
        leaveleft_user_sql = """
        SELECT leave_type, hours FROM leavesystem.leaveleft
        WHERE userID = %s
        AND  leave_type = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(leaveleft_user_sql, (user_id, leave_type_idx))
            leaveleft = cursor.fetchone()
            self.connection.commit()
        leaveleft_dict = {'leave_type': leaveleft[0], 'hours': leaveleft[1]}
        return leaveleft_dict

    def get_creating(self, userID: int, leave_type_idx: int) -> dict:
        """
        Input userID and gets currently applying leaves
        Parameters
        ----------
        userID: [str] The target userID
        leave_type_idx: [int] The leave type to check

        Return
        =========
        Dict of {leaveType: hours}
        -------
        """
        with self.connection.cursor() as cursor:
            check_create_sql = """
                SELECT leave_type, duration FROM leavesystem.create
                WHERE userID = %s
                AND leave_type = %s
            """
            cursor.execute(check_create_sql, (userID, leave_type_idx))
            creating_leave = cursor.fetchall()
            self.connection.commit()
            # Sum the hours of all creating hours
            sum_duration = sum([h[1] for h in creating_leave])

            # fetchall returns tuple of tuples, converting to dict
            creating_dict = {'leave_type': leave_type_idx, 'hours': sum_duration}
        return creating_dict

    def create_leave_getinfo(self, user_id: int) -> dict:
        """
        Input userID return user inforamtion

        Params
        =======
        user_id: userID

        Return
        =======
        Dict of {'blank_info'{'user_id':  'name':  'supervisorID_1':, 'suervisorName_1', 'supervisorID_2':, 'suervisorName_2', 'supervisorID_3': ,'suervisorName_3', 'department': , 'level': , 'leave_remain'DICT/ 'error'(str)}, 'leave_type_dict'}
        """
        # Get set leave
        get_leave_type_sql = """
        SELECT * FROM leavesystem.leavetype
        """
        with self.connection.cursor() as cursor:
            cursor.execute(get_leave_type_sql)
            leave_query = cursor.fetchall()
            self.connection.commit()
        leave_type_dict = [{leave_set[0]: leave_set[1]} for leave_set in leave_query]

        # Get apply user information
        with self.connection.cursor() as cursor:
            create_user_sql = """
            SELECT ID, name, supervisorID_1, supervisorID_2, supervisorID_3, department, level
            FROM leavesystem.users
            WHERE ID = %s
            """
            cursor.execute(create_user_sql, user_id)
            user_info = cursor.fetchone()
            self.connection.commit()

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
                    self.connection.commit()

        # Get user remain leaves -> get leave type dict, find the key(leaveID), build element leave_remain dict of the minus applying leave respectively
        with self.connection.cursor() as cursor:
            # Remain leaves
            today = str(datetime.now().date())
            get_leave_sql = """ 
            SELECT leave_type, hours FROM leavesystem.leaveleft
            WHERE userID = %s
            AND expire >= %s
            """
            # Applying leaves
            get_applied_sql = """
            SELECT leave_type, duration FROM leavesystem.create
            WHERE userID = %s
            """
            cursor.execute(get_leave_sql, (user_id, today))
            leave_remain = cursor.fetchall()
            cursor.execute(get_applied_sql, user_id)
            creating_list = cursor.fetchall()
            self.connection.commit()

        creating_dict = util.add_same_leavetype(creating_list)
        leave_remain_dict = {leave[0]: leave[1] for leave in leave_remain}
        dict_diff = util.leave_dict_diff(leave_remain_dict, creating_dict)
        if dict_diff['status'] == 'valid':
            leave_remain_return = dict_diff['content']
            return {'blank_info': {'user_id': user_info[0], 'name': user_info[1], 'supervisor1': supervisorID_list[0], 'supervisor2': supervisorID_list[1], 'supervisor3': supervisorID_list[2], 'department': user_info[5], 'level': user_info[6], 'leave_remain': leave_remain_return},
                    'leave_type_dict': leave_type_dict}
        else:
            error_message = dict_diff['content']
            return {'blank_info': {'user_id': user_info[0], 'name': user_info[1], 'supervisor1': supervisorID_list[0], 'supervisor2': supervisorID_list[1], 'supervisor3': supervisorID_list[2], 'department': user_info[5], 'level': user_info[6], 'error': error_message},
                    'leave_type_dict': leave_type_dict}

    def create_apply(self, user_id: int, subsituteID: int, start_time: str, end_time: str, leave_type_idx: int, reason: str) -> dict:
        """
        Function after user send out leave application, write to create table and form table

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
        # Get apply leave duration (to hours)
        try:
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M")
            end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
            duration = (end_time - start_time).total_seconds()/3600
        except:
            return {'result': 'failed', 'message': 'create_apply: Cannot transform time format'}

        # Check used leave left minus creating under apply
        leave_left_dict = self.get_leave_left(user_id, leave_type_idx)
        leave_creating_dict = self.get_creating(user_id, leave_type_idx)
        if not leave_creating_dict:
            # There's no creating leaves queried, set the queried leave_type's hours to 0
            leave_creating_dict = {'leave_type': leave_type_idx, 'hours': 0}
        if not leave_left_dict['leave_type'] == leave_creating_dict['leave_type']:  # Check if queried leave type of apply and creating if different, means there's error in code
            return {'result': 'failed', 'message': 'create_apply: Code error, getting different leave_type'}
        else:
            enough_remain_check = leave_left_dict['hours'] - leave_creating_dict['hours']
            if enough_remain_check < 0:
                return {'result': 'failed', 'message': 'create_apply: not enough leave time'}
            else:
                # Able to execute create apply
                # try:
                with self.connection.cursor() as cursor:
                    # Save to leavesystem.create
                    submit_apply_sql = """
                    INSERT INTO leavesystem.create VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
                    """
                    # Save to leavesystem.forms
                    write_to_form_sql = """
                    INSERT INTO leavesystem.forms VALUES(%s, %s, %s, %s, %s, %s, %s, %s);
                    """
                    createID = uuid4()
                    cursor.execute(submit_apply_sql, (createID, user_id, subsituteID, start_time, end_time, duration, leave_type_idx, reason))
                    print(createID, user_id, subsituteID, start_time, end_time, duration, leave_type_idx, reason)
                    signID = uuid4()
                    user_info = global_util.get_user_info(user_id, cursor)
                    print(signID, createID, user_id, user_info['supervisorID_1'], user_info['supervisorID_2'], user_info['supervisorID_3'], 1, 'create')

                    cursor.execute(write_to_form_sql, (signID, createID, user_id, user_info['supervisorID_1'], user_info['supervisorID_2'], user_info['supervisorID_3'], 1, 'create'))
                    self.connection.commit()
                return {'result': 'success', 'message': 'create_apply: success'}

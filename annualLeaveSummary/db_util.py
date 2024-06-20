from datetime import datetime
from global_util.connection_pool import POOL
from global_util import global_util


class DbOperator:
    def __init__(self):
        connection = POOL.connection()
        this_year = datetime.now()
        self.connection = connection
        self.current_year = datetime.today().year

        check_overtime_leave_table_sql = """
             SELECT TABLE_NAME FROM information_schema.tables
            WHERE TABLE_SCHEMA = 'leavesystem'
            AND TABLE_NAME = 'overtime'
            """
        with connection.cursor() as cursor:
            cursor.execute(check_overtime_leave_table_sql)
            overtime_table_check = cursor.fetchone()
            connection.commit()

        if overtime_table_check is None:
            create_overtime_leave_table = """
                CREATE TABLE IF NOT EXISTS leavesystem.overtime(
                ID INT NOT NULL AUTO_INCREMENT,
                userID BIGINT NOT NULL,
                start_time datetime,
                end_time datetime,
                expire datetime,
                hours float,
                reason text,
                PRIMARY KEY (ID)
                ) AUTO_INCREMENT = 1
                """
            with connection.cursor() as cursor:
                cursor.execute(create_overtime_leave_table)
                connection.commit()

    def get_init_expire(self, user_id) -> tuple:
        """
        Function to get the last exprie date fo current year's annual leave
        Parameters
        ----------
        user_id: [int] The user to query from

        Returns
        -------
        Annual leave given date, Annual leave expire date
        """
        init_expire_sql = """
            SELECT given, expire from leavesystem.leaveleft
            WHERE leave_type = 1
            AND userID = %s
            AND expire <= %s
            AND given >=%s
            ORDER BY expire DESC
            """
        with self.connection.cursor() as cursor:
            cursor.execute(init_expire_sql, (user_id, str(self.current_year) + '-12-31', str(self.current_year - 1) + '-01-01'))
            given_expire = cursor.fetchone()
            self.connection.commit()
        if given_expire is not None:
            format_given = given_expire[0].strftime("%Y-%m-%d")
            format_expire = given_expire[1].strftime("%Y-%m-%d")
            return format_given, format_expire
        else:
            return None, None

    def get_frame_data(self, user_id: int):
        """
        The data of all used leaves
        Parameters
        ----------
        user_id: [int] The user id to query from

        Returns
        -------
        Json of the data
        """
        annual_leave_summary = """
            SELECT start_time, end_time, hours, leave_type, reason
            FROM leavesystem.leaveused
            WHERE userID = %s
            ORDER BY end_time DESC
            """
        with self.connection.cursor() as cursor:
            cursor.execute(annual_leave_summary, user_id)
            data = cursor.fetchall()

        with self.connection.cursor() as cursor:
            leavetype_dict = global_util.get_leavetype_collate(cursor, 'chinese')
        formatted_data = []
        for leave in data:
            format_leave = {'start_time': leave[0].strftime('%Y-%m-%d %H:%M:%S'), 'end_time': leave[1].strftime('%Y-%m-%d %H:%M:%S'), 'hours': leave[2], 'leave_type': leavetype_dict[leave[3]], 'reason': leave[4]}
            formatted_data += [format_leave]
        return formatted_data

    def get_user_name(self, user_id: int) -> str:
        """
        Simple get user's name
        Parameters
        ----------
        user_id: [int] The user id to query

        Returns
        -------
        The user's name
        """
        with self.connection.cursor() as cursor:
            name = global_util.get_user_info(user_id, cursor)['name']
        return name

    def get_overtime_detail(self, user_id: int) -> list:
        """
        Get list of dictionary of overtime detail
        Parameters
        ----------
        user_id: [int] The user id to query

        Return
        -------
        list of dict of overtime detail
        """
        with self.connection.cursor() as cursor:
            get_overtime_detail_sql = """
                SELECT start_time, end_time, hours, reason FROM leavesystem.overtime
                where userID = %s
                ORDER BY end_time DESC
                """
            cursor.execute(get_overtime_detail_sql, user_id)
            overtime_data = cursor.fetchall()
            self.connection.commit()
        formatted_overtime_data = []
        for line in overtime_data:
            d = {'start_time': line[0].strftime("%Y-%m-%d %H:%M:%S"), 'end_time': line[1].strftime("%Y-%m-%d %H:%M:%S"), 'hours': line[2], 'reason': line[3]}
            formatted_overtime_data += [d]
        return formatted_overtime_data

    def get_overtime_total(self, user_id: int) -> float:
        """
        Get total amount of the overtime acquired
        Parameters
        ----------
        user_id: [int] The user id to query

        Return
        -------
        Amount of total overtime
        """
        get_overtime_total_sql = """
            SELECT SUM(hours)
            FROM leavesystem.leaveleft
            WHERE userID = %s
            AND leave_type = 12
            """
        with self.connection.cursor() as cursor:
            cursor.execute(get_overtime_total_sql, user_id)
            overtime_total = cursor.fetchone()[0]
        return overtime_total or 0

    def get_overtime_remain(self, user_id: int) -> float:
        """
        Get the subtraction of acquired overtime leave and minus used overtime leave
        Parameters
        ----------
        user_id: [int] The user id to query

        Return
        -------
        Amount of total overtime leave remains
        """
        overtime_total = self.get_overtime_total(user_id)
        used_overtime_sql = """
            SELECT SUM(hours)
            FROM leavesystem.leaveused
            WHERE userID = %s
            AND leave_type = 12
            """
        with self.connection.cursor() as cursor:
            cursor.execute(used_overtime_sql, user_id)
            used_overtime = cursor.fetchone()[0]
            self.connection.commit()
        overtime_remain = overtime_total - (used_overtime or 0)
        return overtime_remain


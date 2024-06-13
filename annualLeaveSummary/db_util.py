from datetime import datetime
from global_util.connection_pool import POOL
from global_util.global_util import get_leavetype_collate


class DbOperator:
    def __init__(self):
        connection = POOL.connection()
        this_year = datetime.now()
        self.connection = connection
        self.current_year = datetime.today().year

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
            """
        with self.connection.cursor() as cursor:
            cursor.execute(annual_leave_summary, user_id)
            data = cursor.fetchall()

        with self.connection.cursor() as cursor:
            leavetype_dict = get_leavetype_collate(cursor, 'chinese')
        # Convert data to desired type
        formatted_data = [
            (leave[0].strftime('%Y-%m-%d'), leave[1].strftime('%Y-%m-%d'), leave[2], leavetype_dict[leave[3]], leave[4]) for leave
            in data]

        return formatted_data
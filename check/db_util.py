from global_util.connection_pool import POOL
from datetime import datetime
from global_util.global_util import get_leavetype_collate


class DbOperator:
    def __init__(self):
        self.connection = POOL.connection()
        self.current_year = datetime.now().year
        # Check leavetype table syntext of MySQL
        with self.connection.cursor() as cursor:
            check_leave_type = """
                   SELECT TABLE_NAME FROM information_schema.tables
                   WHERE TABLE_SCHEMA = 'leavesystem'
                   AND TABLE_NAME = 'leaveused'
                   """
            cursor.execute(check_leave_type)
            check_check = cursor.fetchone()
        if check_check is None:
            create_leave_used_sql = """
                    CREATE TABLE IF NOT EXISTS leavesystem.leaveused(
                    userID BIGINT NOT NULL,
                    leave_type INT,
                    start_time DATETIME,
                    end_time DATETIME,
                    hours float,
                    applyID varchar(255)
                    )
                    """
            with self.connection.cursor() as cursor:
                cursor.execute(create_leave_used_sql)
        self.connection.commit()

    def get_current_year_annual_leave(self, user_id: int) -> float:
        """
        Gets current year's annual leave amount

        Parameters
        =========
        user_id: [int] The user's ID

        Return
        =========
        Current year's leave amount [float]
        """
        with self.connection.cursor() as cursor:
            current_year_annal_leave_sql = """
                SELECT sum(hours) from leavesystem.leaveleft
                WHERE userID = %s
                AND leave_type = 1
                AND expire between %s and %s
                """
            cursor.execute(current_year_annal_leave_sql, (user_id, str(self.current_year + 1) + '-01-01', str(self.current_year + 1) + '-12-31'))
            current_year_annal_leave_amt = cursor.fetchone()[0]
        self.connection.commit()
        return current_year_annal_leave_amt

    def get_last_year_annual_leave(self, user_id: int) -> float:
        """
        Gets last year's annual leave amount

        Parameters
        =========
        user_id: [int] The user's ID

        Return
        =========
        Last year's leave amount [float]
        """
        with self.connection.cursor() as cursor:
            last_year_annal_leave_sql = """
                SELECT sum(hours) from leavesystem.leaveleft
                WHERE userID = %s
                AND leave_type = 1
                AND expire between %s and %s
                """
            cursor.execute(last_year_annal_leave_sql, (user_id, str(self.current_year) + '-01-01', str(self.current_year) + '-12-31'))
            last_year_annal_leave_amt = cursor.fetchone()[0]
        self.connection.commit()
        return last_year_annal_leave_amt

    def get_current_year_expire(self, user_id: int) -> str | None:
        with self.connection.cursor() as cursor:
            """
            Get the expiry date of annual leave of this year(which can be use this year)

            Parameter
            ==========
            user_id: [int] The user's ID

            Return
            =========
            The Expire date 
            """
            current_expire_date_sql = """
                SELECT expire FROM leavesystem.leaveleft
                WHERE userID = %s
                AND expire between %s and %s
                """
            cursor.execute(current_expire_date_sql, (user_id, str(self.current_year + 1) + '-01-01', str(self.current_year + 1) + '-12-31'))
            this_year_expire = cursor.fetchone()
            self.connection.commit()
            if this_year_expire:
                this_year_expire_format = this_year_expire[0].strftime("%Y-%m-%d")
                return this_year_expire_format
            else:
                return None

    def get_last_year_expire(self, user_id) -> str | None:
        """
        Get the expiry date of annual leave of last year(which can be use or inherit to this year)

        Parameter
        ==========
        user_id: [int] The user's ID

        Return
        =========
        The Expire date
        """
        with self.connection.cursor() as cursor:
            last_expire_date_sql = """
                       SELECT expire FROM leavesystem.leaveleft
                       WHERE userID = %s
                       AND expire between %s and %s
                       """
            cursor.execute(last_expire_date_sql, (user_id, str(self.current_year) + '-01-01', str(self.current_year) + '-12-31'))
            last_year_expire = cursor.fetchone()
            self.connection.commit()
        if last_year_expire:
            last_year_expire_format = last_year_expire[0].strftime("%Y-%m-%d")
            return last_year_expire_format
        else:
            return None

    def get_overtime_total(self, user_id) -> float:
        """
        Get unuse and used overtime leave

        Parameter
        ==========
        user_id: [int] The user's ID

        Return
        =========
        The float of total gained overtime leave
        """
        # Leave type of overtime leave is 12
        with self.connection.cursor() as cursor:
            overtime_unuse_sql = """
                SELECT sum(hours) FROM leavesystem.leaveleft
                WHERE leave_type = 12
                AND userID = %s
                """
            cursor.execute(overtime_unuse_sql, user_id)
            overtime_total_unuse = cursor.fetchone()[0]

            overtime_used_sql = """
                SELECT sum(hours) FROM leavesystem.leaveused
                WHERE leave_type = 12
                AND userID = %s
                """
            cursor.execute(overtime_used_sql, user_id)
            overtime_total_used = cursor.fetchone()[0]
            self.connection.commit()
        total = (overtime_total_unuse if overtime_total_unuse is not None else 0) + (overtime_total_used if overtime_total_used is not None else 0)
        return total

    def get_over_time_used(self, user_id: int) -> float:
        """
        Gets used overtime leave

        Parameters
        ----------
        user_id: [int] The user's ID

        Returns
        -------
        The float of used overtime leave
        """
        # Leave type of overtime leave is 12
        with self.connection.cursor() as cursor:
            used_overtime_sql = """
                SELECT sum(hours) FROM leavesystem.leaveused
                WHERE userID = %s
                AND leave_type = 12
                """
            cursor.execute(used_overtime_sql, user_id)
            used_overtime_leave = cursor.fetchone()[0]
            self.connection.commit()
        return used_overtime_leave if used_overtime_leave is not None else 0

    def get_overtime_remain(self, user_id: int) -> float:
        """
        Gets remain overtime leave
        Parameters
        ----------
        user_id: [int] The user's ID

        Returns
        -------
        The float of remain overtime leave
        """
        with self.connection.cursor() as cursor:
            today = str(datetime.now().date())
            remain_overtime_sql = """
                SELECT sum(hours) FROM leavesystem.leaveleft
                WHERE leave_type = 12
                AND userID = %s
                AND expire > %s
                """
            cursor.execute(remain_overtime_sql, (user_id, today))
            remain_overtime = cursor.fetchone()[0]
            self.connection.commit()
        return remain_overtime if remain_overtime is not None else 0

    def get_overtime_overdue(self, user_id: int) -> float | None:
        """
        Gets the expired overtime leave

        Parameters
        ----------
        user_id: [int] The user's ID

        Returns
        -------
        The expired hours of the user
        """
        today = datetime.now().date()
        with self.connection.cursor() as cursor:
            expried_overtime_sql = """
                SELECT sum(hours) FROM leavesystem.leaveleft
                WHERE leave_type = 12
                AND userID = %s
                AND expire < %s 
                """
            cursor.execute(expried_overtime_sql, (user_id, today))
            overdue_hours = cursor.fetchone()[0]
            self.connection.commit()
        return overdue_hours if overdue_hours is not None else 0

    def get_recent_used(self, user_id: int) -> list[dict]:
        """
        Gets recent 3 approved leaves

        Parameters
        ----------
        user_id: [int] The user's ID

        Returns
        -------
        A list of recent 3 used leave, format as below
        [{leave_type:
        leave_start:
        leave_end:
        duration:},
        ...]
        """
        # Get recent 3 leaves
        with self.connection.cursor() as cursor:
            top_3_used_sql = """
                SELECT leave_type, start_time, end_time, hours FROM leavesystem.leaveused
                WHERE userID = %s
                ORDER BY start_time
                LIMIT 3
                """
            cursor.execute(top_3_used_sql, user_id)
            used_leaves = cursor.fetchall()

            # Get leave type to collate to chinese
            leave_collate = get_leavetype_collate(cursor, 'chinese')

            self.connection.commit()

            # Gets the correct format
            leave_list = []
            if used_leaves is not None:
                for leave in used_leaves:
                    single_leave_dict = {'leavetype': leave_collate[leave[0]], 'start_time': leave[1], 'end_time': leave[2], 'duration': leave[3]}
                    leave_list += [single_leave_dict]
            return leave_list


from global_util.connection_pool import POOL
from datetime import datetime

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
        # TODO: This function is not tested
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
            cursor.execute(overtime_unuse_sql, user_id)
            overtime_total_used = cursor.fetchone()[0]
            self.connection.commit()
        total = overtime_total_unuse + overtime_total_used
        return total

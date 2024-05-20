from global_util.connection_pool import POOL
from datetime import datetime

class DbOperator:
    def __init__(self):
        self.connection = POOL.connection()
        self.current_year = datetime.now().year

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

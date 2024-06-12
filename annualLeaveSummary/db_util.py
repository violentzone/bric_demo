from datetime import datetime
from global_util.connection_pool import POOL



class DbOperator:
    def __init__(self):
        connection = POOL.connection()
        this_year = datetime.now()
        self.connection = connection
        self.current_year = datetime.today().year

    def get_init_expire(self, user_id) -> tuple:
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
        annual_leave_summary = """
            SELECT start_time, end_time, duration, 
            """
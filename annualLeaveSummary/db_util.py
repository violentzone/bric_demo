from datetime import datetime
from global_util.connection_pool import POOL


class DbOperator:
    def __init__(self):
        connection = POOL.connection()
        this_year = datetime.now()
        self.connection = connection

    def get_init_expire(self):
        init_expire_sql = """
            SELECT given, expire from leavesystem.leaveleft
            WHERE leave_type = 1
            AND expire 
            """
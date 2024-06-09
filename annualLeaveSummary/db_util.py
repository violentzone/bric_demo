import pymysql
from global_util.connection_pool import POOL


class DbOperator:
    def __init__(self):
        connection = POOL.connection()

        self.connection = connection

    def get_init_expire(self):
        init_expire_sql = """
            SELECT 
            """
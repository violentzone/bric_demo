import pymysql
from global_util.connection_pool import POOL
class DbOperator:
    """
    Init of home page which show forms to sign
    create leaveSystem.froms if not exists
    """
    def __init__(self):

        connection = POOL.connection()

        # check if leavesystem.forms exists
        check_sql = """
        SELECT * FROM leavesystem.forms
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(check_sql)
                connection.commit()

        except:
            # Create leavesystem.forms
            create_forms_sql = """
            CREATE TABLE IF NOT EXISTS leavesystem.forms(
            ID varchar(255) NOT NULL,
            formID varchar(255) NOT NULL,
            userid BIGINT,
            signer1 BIGINT,
            signer2 BIGINT,
            signer3 BIGINT,
            status BIGINT,
            type text,
            PRIMARY KEY (ID)
            )
            """
            with connection.cursor() as cursor:
                cursor.execute(create_forms_sql)
                connection.commit()

        finally:
            self.connection = POOL.connection()


    def id_to_name(self, user_id: int):
        user2name_sql = """
        SELECT name FROM leavesystem.users
        WHERE ID = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(user2name_sql, user_id)
            name = cursor.fetchone()[0]
            self.connection.commit()
        return name

    def unsign_num(self, user_id):
        unsign_sql = """
        SELECT count(ID) FROM leavesystem.forms WHERE userid = %s AND status <> 0
        """
        with self.connection.cursor() as cursor:
            cursor.execute(unsign_sql, user_id)
            form_count = cursor.fetchone()
        self.connection.commit()
        return form_count[0]


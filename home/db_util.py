from loguru import logger
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
            signer1_status boolean,
            signer2 BIGINT,
            signer2_status boolean,
            signer3 BIGINT,
            signer3_status boolean,
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
        # Log
        logger.bind(user_id=user_id).info(f'Function: {__name__}')
        return form_count[0]


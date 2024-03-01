import pymysql
from json import loads
class DbOperator:
    """
    Init of home page which show forms to sign
    create leaveSystem.froms if not exists
    """
    def __init__(self):
        with open('infos/db.json') as f:
            db_config = loads(f.read())
        connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'], database='leavesystem')

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
            CREATE TABLE IF NOT EXISTS leavsystem.forms(
            ID varchar(255) NOT NULL,
            userid BIGINT,
            type text,
            PRIMARY KEY (ID)
            )
            """
            with connection.cursor() as cursor:
                cursor.execute(create_forms_sql)
                connection.commit()

        finally:
            self.connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'], database='leavesystem')

    def unsign_num(self, user_id):
        unsign_sql = """
        SELECT count(ID) FROM leavesystem.forms WHERE userid = %s 
        """
        with self.connection.cursor() as cursor:
            cursor.execute(unsign_sql, user_id)
            form_count = cursor.fetchone()
        return form_count[0]


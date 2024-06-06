from pymysql.cursors import Cursor
from json import loads
from typing import Literal


def get_user_info(userID: int, cursor: Cursor) -> dict:
    sql = """
    SELECT ID, userName, name, supervisorID_1, supervisorID_2, supervisorID_3, department, level
    from leavesystem.users
    where ID = %s
    """
    cursor.execute(sql, userID)
    user_info = cursor.fetchone()

    return {"ID": user_info[0], 'userName': user_info[1], 'name': user_info[2], 'supervisorID_1': user_info[3],
            'supervisorID_2': user_info[4], 'supervisorID_3': user_info[5], 'department': user_info[6], 'level': user_info[7]}


def get_leavetype_collate(cursor: Cursor, language: Literal['chinese', 'english']) -> dict:
    """
    Gets collation of MySql db

    Parameters
    ----------
    cursor: The pymysql cursor, should operate inside `with connection.cursor() as cursor:`
    language: The target language to collate from, only support chinese and english

    Returns
    -------
    The dict of leave type and it's chinese or english collation
    """
    sql = """
        SELECT * FROM leavesystem.leavetype
        """
    cursor.execute(sql)
    leavetype = cursor.fetchall()

    if language == 'chinese':
        idx = 1
    else:
        idx = 2
    # Convert to dict of index: translation
    leavetype_format = {_[0]: _[idx] for _ in leavetype}
    return leavetype_format

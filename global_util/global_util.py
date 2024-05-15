import pymysql
from json import loads


def get_user_info(userID: int, cursor) -> dict:
    sql = """
    SELECT ID, userName, name, supervisorID_1, supervisorID_2, supervisorID_3, department, level
    from leavesystem.users
    where ID = %s
    """
    cursor.execute(sql, userID)
    user_info = cursor.fetchone()

    return {"ID": user_info[0], 'userName': user_info[1], 'name': user_info[2], 'supervisorID_1': user_info[3],
            'supervisorID_2': user_info[4], 'supervisorID_3': user_info[5], 'department': user_info[6], 'level': user_info[7]}

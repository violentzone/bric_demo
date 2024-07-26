from loguru import logger
import os
from functools import wraps
from flask_jwt_extended import get_jwt_identity

from global_util.global_util import get_user_list
from global_util.connection_pool import POOL

LOG_DIR = 'api_log'
# Set to False when production
DIAGNOSE = True


## Depretcated
# def make_user_log():
#     pool = POOL
#     # Get all exists users
#     with pool.connection().cursor() as cursor:
#         user_list = get_user_list(cursor)
#
#     # Set up a main log file to log something not by user
#     user_list += ['main']
#
#     # Make log file
#     for user_id in user_list:
#         if not os.path.exists('user_log/{str(user_id)}.log'):
#             logger.add(f'user_log/{str(user_id)}.log', filter=lambda record: record['extra']['user_id'] == user_id, rotation='100 MB')


def log_init():
    """
    Creates loging directory
    Returns
    -------
    None
    """
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)


# Log decorator
def log_action(_logger: logger):
    def decorator(fun):
        @wraps(fun)
        def wrapper(*args, **kwargs):
            # Gets username
            user_name = get_jwt_identity()
            logger.info(f'{user_name}: {__name__}, args: {str(*args, **kwargs)}')
            return fun(*args, **kwargs)
        return wrapper
    return decorator

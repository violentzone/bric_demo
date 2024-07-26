from loguru import logger
from json import loads
import os

from global_util.global_util import get_user_list
from global_util.connection_pool import POOL

LOG_DIR = 'user_log'


def make_user_log():
    pool = POOL
    # Get all exists users
    with pool.connection().cursor() as cursor:
        user_list = get_user_list(cursor)

    # Make log file
    for user_id in user_list:
        if not os.path.exists('user_log/{str(user_id)}.log'):
            logger.add(f'user_log/{str(user_id)}.log', filter=lambda record: record['extra']['user_id'] == user_id, rotation='100 MB')


def log_init():
    """
    Creates loging directory
    Returns
    -------
    None
    """
    if not os.path.exists(LOG_DIR):
        os.mkdir(LOG_DIR)

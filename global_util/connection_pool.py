from dbutils.pooled_db import PooledDB
import pymysql
from json import loads

# Get config setting
with open('infos/db.json') as f:
    config_setting = loads(f.read())

# Establis connection pool
POOL = PooledDB(pymysql, host=config_setting['url'], user=config_setting['user'], password=config_setting['password'], database=config_setting['database'])

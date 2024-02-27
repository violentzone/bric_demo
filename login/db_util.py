""" Utility of te, containing create, verify passwords etc"""
import pymysql
from json import loads
from passlib.hash import pbkdf2_sha256
from datetime import datetime

class DbOperator:
    def __init__(self):

        """
        Init, check if able to te and create database 'leavesystem' if not exists
        """
        # Get json config
        with open('infos/db.json') as f:
            db_config = loads(f.read())
        try:
            self.connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'], database='leavesystem')

        # If there's no db
        except:
            if_database ="""
            CREATE DATABASE IF NOT EXISTS leavesystem;"""

            # Prepare information for admin at the first establishment
            admin_password = pbkdf2_sha256.hash('admin', salt=b'begin')
            create_admin_time = datetime.now()

            if_table = """
            CREATE TABLE IF NOT EXISTS leavesystem.users (
            ID BIGINT NOT NULL AUTO_INCREMENT,
            userName text,
            hashpassword varchar(255),
            createdate datetime,
            PRIMARY KEY (ID) 
            );"""

            add_user = """
            INSERT INTO leavesystem.users VALUES (1, 'admin', %s, %s);
            """

            connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'])
            with connection.cursor() as cursor:
                cursor.execute(if_database)
                cursor.execute(if_table)
                cursor.execute(add_user, (admin_password, create_admin_time))
                connection.commit()

            self.connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'], database='leavesystem')

    def login_check(self, user_name: str, password: str) -> bool:
        user_info_sql = """
        SELECT userName, hashpassword FROM leavesystem.users where userName = %s
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(user_info_sql, user_name)
                user_info = cursor.fetchone()
        except:
            ValueError('Cannot query user information during te check')
        # Check if gets anything
        if user_info is None:
            return False

        # Check if password can verify
        if pbkdf2_sha256.verify(password, user_info[1]):
            return True
        else:
            return False

    def create_user(self, user_name: str, password: str) -> bool:

        # Check if any identical userName in db
        check_exists_sql = """
        SELECT EXISTS (SELECT userName FROM leavesystem.users where userName = %s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(check_exists_sql, user_name)
            check_exists = cursor.fetchone()[0]

        if check_exists == 1:
            return False
        else:
            password_hash = pbkdf2_sha256.hash(password, salt=b'the_salt')
            create_time = datetime.now()
            insert_user_sql = """
            INSERT INTO leavesystem.users (userName, hashpassword, createdate) VALUES (%s, %s, %s)"""

            with self.connection.cursor() as cursor:
                cursor.execute(insert_user_sql, (user_name, password_hash, create_time))
                self.connection.commit()
            return True

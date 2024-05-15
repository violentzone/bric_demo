""" Utility of te, containing create, verify passwords etc"""
import pymysql
from json import loads
from passlib.hash import pbkdf2_sha256
from datetime import datetime
from global_util.connection_pool import POOL

class DbOperator:
    def __init__(self):

        """
        Init, check if able to te and create database 'leavesystem' if not exists
        """
        try:
            self.connection = POOL.connection()

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
            userName varchar(255),
            name text,
            hashpassword varchar(255),
            supervisorID_1 BIGINT,
            supervisorID_2 BIGINT,
            supervisorID_3 BIGINT,
            createdate datetime,
            department varchar(255),
            level int,
            PRIMARY KEY (ID) 
            );"""

            add_user = """
            INSERT INTO leavesystem.users VALUES (1, 'admin', 'admin', %s, null, null, null, %s, '0000', 0);
            """

            connection = POOL.connection()
            with connection.cursor() as cursor:
                cursor.execute(if_database)
                cursor.execute(if_table)
                cursor.execute(add_user, (admin_password, create_admin_time))
                connection.commit()

            self.connection = POOL.connection()

    def login_check(self, user_name: str, password: str) -> bool:
        user_info_sql = """
        SELECT userName, hashpassword FROM leavesystem.users where userName = %s
        """

        with self.connection.cursor() as cursor:
            cursor.execute(user_info_sql, user_name)
            user_info = cursor.fetchone()

        # Check if gets anything
        if user_info is None:
            return False

        # Check if password can verify
        if pbkdf2_sha256.verify(password, user_info[1]):
            return True
        else:
            return False


    def user_info(self, username: str):
        user_to_id_sql = """
        SELECT ID, username FROM leavesystem.users WHERE username = %s
        """
        with self.connection.cursor() as cursor:
            cursor.execute(user_to_id_sql, username)
            user = cursor.fetchone()
            userID = user[0]
            username = user[1]
        return  userID, username

    def create_user(self, user_name: str, password: str, name: str, supervisorID_1: int, supervisorID_2: int, supervisorID_3: int, level: int, dept: str) -> bool:

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
            INSERT INTO leavesystem.users (userName, name, hashpassword, supervisorID_1, supervisorID_2, supervisorID_3, createdate, level, department) VALUES (%s, %s ,%s, %s, %s, %s, %s, %s, %s)"""

            with self.connection.cursor() as cursor:
                cursor.execute(insert_user_sql, (user_name, name, password_hash, supervisorID_1, supervisorID_2, supervisorID_3, create_time, level, dept))
                self.connection.commit()
            return True

    def logon_check(self):
        self.connection.ping(reconnect=True)
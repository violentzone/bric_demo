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
            if_database = """
            CREATE DATABASE IF NOT EXISTS leavesystem;"""

            # Prepare information for admin at the first establishment
            admin_password = pbkdf2_sha256.hash('admin', salt=b'begin')
            ray_password = pbkdf2_sha256.hash('1234', salt=b'begin')
            yin_password = pbkdf2_sha256.hash('1234', salt=b'begin')
            create_admin_time = datetime.now()

            if_table = """
            CREATE TABLE IF NOT EXISTS leavesystem.users (
            ID BIGINT NOT NULL,
            userName varchar(255),
            name text,
            hashpassword varchar(255),
            substitute BIGINT,
            supervisorID_1 BIGINT,
            supervisorID_2 BIGINT,
            supervisorID_3 BIGINT,
            createdate datetime,
            ID_number varchar(20),
            department varchar(255),
            level int,
            PRIMARY KEY (ID) 
            );"""

            add_user = """
            INSERT INTO leavesystem.users VALUES (1, 'admin', 'admin', %s, null, null, null, null, %s, 'A123456789','0000', 0), (2, 'ray', 'Ray', %s, 1, 1, null, null, %s, 'A123456787','0001', 1), (3, 'yin', 'Yin', %s, 2, 2, 1, null, %s, 'E124218661','0001', 2);
            """
            with open('infos/db.json') as f:
                config_setting = loads(f.read())
            connection = pymysql.connect(host=config_setting['url'], user=config_setting['user'], password=config_setting['password'])
            with connection.cursor() as cursor:
                cursor.execute(if_database)
                cursor.execute(if_table)
                cursor.execute(add_user, (admin_password, create_admin_time, ray_password, create_admin_time, yin_password, create_admin_time,))
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
        print(user_info)
        print(pbkdf2_sha256.verify(password, user_info[1]))
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
            self.connection.commit()
            user = cursor.fetchone()
            userID = user[0]
            username = user[1]
        return  userID, username

    def create_user(self, user_id: int, user_name: str, password: str, substitute: int, name: str, identification: str, supervisorID_1: int, supervisorID_2: int, supervisorID_3: int, dept: str) -> bool:
        """
        Returns True if successfully create user, else return False

        Parameters
        ----------
        user_id: [int] The employee ID
        user_name:[str] The account of the employee to login
        password:[str] The password to login
        substitute: [int] The substitute of that employee
        name:[str] The name display on top of the webpage
        identification: [str] The ID of the person
        supervisorID_1:[int] The primary supervisor, None if company leader
        supervisorID_2:[int] The secondary supervisor, None if department leader
        supervisorID_3:[int] The third supervisor, None if team leader
        dept: [str] Department

        Returns
        -------
        True if succeed, else False
        """
        # Check if any identical userName in db
        print('substitute:', substitute, 'supervisorID_2: ', type(supervisorID_2))
        check_exists_sql = """
        SELECT EXISTS (SELECT userName FROM leavesystem.users where userName = %s)
        """
        with self.connection.cursor() as cursor:
            cursor.execute(check_exists_sql, user_name)
            check_exists = cursor.fetchone()[0]
            self.connection.commit()

        if check_exists == 1:
            return False

        else:
            password_hash = pbkdf2_sha256.hash(password, salt=b'the_salt')

            # Employee level determination
            if supervisorID_3 is None:
                if supervisorID_2 is None:
                    if supervisorID_1 is None:
                        level = 0
                    else:
                        level = 1
                else:
                    level = 2
            else:
                level = 3

            create_time = datetime.now()
            insert_user_sql = """
            INSERT INTO leavesystem.users (ID, userName, name, hashpassword, substitute, supervisorID_1, supervisorID_2, supervisorID_3, createdate, ID_number ,level, department) VALUES (%s, %s ,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""

            with self.connection.cursor() as cursor:
                cursor.execute(insert_user_sql, (user_id, user_name, name, password_hash, substitute, supervisorID_1, supervisorID_2, supervisorID_3, create_time, identification, level, dept))
                self.connection.commit()
            return True

    def check_user(self, user_id: int) -> bool:
        check_exists_sql = """
            SELECT EXISTS(SELECT * FROM leavesystem.users WHERE ID = %s)
            """
        with self.connection.cursor() as cursor:
            cursor.execute(check_exists_sql, user_id)
            ans = cursor.fetchone()[0]
        if ans:
            return True
        else:
            return False

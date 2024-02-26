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
        self.connection = pymysql.connect(host=db_config['url'], user=db_config['user'], password=db_config['password'])
        if_database ="""
        CREATE DATABASE IF NOT EXISTS leavesystem;"""
        if_table="""
        CREATE TABLE IF NOT EXISTS leavesystem.users (
        ID BIGINT NOT NULL AUTO_INCREMENT,
        userName text,
        hashpassword varchar(255),
        createdate datetime,
        PRIMARY KEY (ID) 
        );
        """
        with self.connection.cursor() as cursor:
            cursor.execute(if_database)
            cursor.execute(if_table)
            self.connection.commit()


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
        # Check if get anything
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
            check_exists = cursor.fetchone()

        if check_exists:
            return False
        else:
            password_hash = pbkdf2_sha256.hash(password, salt=b'the_salt')
            create_time = datetime.now()
            insert_user_sql = """
            INSERT INTO leavesystem.users (userName, hashpassword, createdate) VALUES(%s, %s, %s)"""

            with self.connection.cursor() as cursor:
                cursor.execute(insert_user_sql, (user_name, password_hash, create_time))
                self.connection.commit()
            return True

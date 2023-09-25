import os
import time

import pymysql.cursors

from backend.log import get_logger
from backend.schemas.user import User, UserInDB, UserToDB

from .init_db import create_tables

logger = get_logger(__name__)


def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT")),
        database=os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_ROOT_USER"),
        password=os.getenv("MYSQL_ROOT_PASSWORD"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


ready = False
retry = 60
while not ready:
    try:
        conn = get_connection()
        ready = True
    except Exception as e:
        logger.info(f"trying to connect to bd...\n{e}")
        time.sleep(3)
        retry -= 1
        if not retry:
            msg = "Maximum number of db connection retries exceeded"
            logger.error(msg)
            raise RuntimeError(msg)

create_tables(conn)


def get_dbcursor():
    return conn


def is_user_exist(username: str) -> bool:
    cursor = conn.cursor()
    query = """ SELECT username
                FROM users
                WHERE username=%s;
            """
    cnt = cursor.execute(query, (username))
    return True if cnt else False


def insert_into_user(user: UserToDB) -> User:
    cursor = conn.cursor()
    query = """ INSERT INTO users (
                    username,
                    first_name,
                    last_name,
                    age,
                    bio,
                    city,
                    country,
                    password,
                    disabled)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
    cursor.execute(
        query,
        (
            user.username,
            user.first_name,
            user.last_name,
            user.age,
            user.bio,
            user.city,
            user.country,
            user.password,
            user.disabled,
        ),
    )
    conn.commit()
    user.id = cursor.lastrowid
    cursor.close()
    return user


def get_user_by_username(username: str) -> UserInDB | None:
    cursor = conn.cursor()
    query = """ SELECT *
                FROM users
                WHERE username=%s;
            """
    cursor.execute(query, (username))
    user_dict = cursor.fetchone()
    cursor.close()
    return UserInDB(**user_dict) if user_dict else None


def get_user_by_id(id: int | str) -> UserInDB | None:
    cursor = conn.cursor()
    query = """ SELECT *
                FROM users
                WHERE id=%s;
            """
    cursor.execute(query, (int(id)))
    user_dict = cursor.fetchone()
    cursor.close()
    return UserInDB(**user_dict) if user_dict else None


def search_user(first_name: str, last_name: str) -> UserInDB | None:
    cursor = conn.cursor()
    query = """ SELECT *
                FROM users
                WHERE first_name LIKE %s AND last_name LIKE %s ;
            """
    cursor.execute(query, (f"%{first_name}%", f"%{last_name}%"))
    users_dict = cursor.fetchall()
    cursor.close()
    return [UserInDB(**user_dict) for user_dict in users_dict]

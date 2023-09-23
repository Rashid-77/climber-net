import os
import time
import pymysql.cursors

from backend.schemas.user import User
from .init_db import create_tables
from backend.log import get_logger


logger = get_logger(__name__)


def get_connection():
    return pymysql.connect(
            host=os.getenv('MYSQL_HOST'),
            port=int(os.getenv('MYSQL_PORT')),
            database=os.getenv('MYSQL_DATABASE'),
            user=os.getenv('MYSQL_ROOT_USER'),
            password=os.getenv('MYSQL_ROOT_PASSWORD'),
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )


ready = False
retry = 60
while not ready:
    try:
        conn = get_connection()
        ready = True
    except Exception as e:
        logger.info(f'trying to connect to bd...\n{e}')
        time.sleep(3)
        retry -= 1
        if not retry:
            msg = 'Maximum number of db connection retries exceeded'
            logger.error(msg)
            raise RuntimeError(msg)

create_tables(conn)


def get_dbcursor():
    return conn


def is_user_exist(username: str) -> bool:
    cursor = conn.cursor()
    query = ''' SELECT username
                FROM users
                WHERE username=%s;
            '''
    cnt = cursor.execute(query, (username))
    return True if cnt else False


def insert_into_user(user: User) -> User:
    cursor = conn.cursor()
    query = ''' INSERT INTO users (
                    username,
                    first_name,
                    last_name,
                    age,
                    bio,
                    city,
                    country,
                    password)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            '''
    cursor.execute(query, (user.username,
                           user.first_name,
                           user.last_name,
                           user.age,
                           user.bio,
                           user.city,
                           user.country,
                           user.password)
    )
    logger.debug(f'{cursor.lastrowid=}')
    conn.commit()
    user.id = cursor.lastrowid
    logger.debug(f'{cursor.lastrowid=}')
    cursor.close()

import os
import time

from backend.log import get_logger
from backend.schemas.user import User, UserInDB, UserToDB
from backend.utils.config import get_settings

logger = get_logger(__name__)
logger.info('db.py started')

def get_connection():
    logger.info('-> get_connection()')
    # if os.getenv("DB") == 'mysql':
    #     logger.info('mysql get_connection()')
    #     import pymysql.cursors
    #     return pymysql.connect(
    #         host=os.getenv("MYSQL_HOST"),
    #         port=int(os.getenv("MYSQL_PORT")),
    #         database=os.getenv("MYSQL_DATABASE"),
    #         user=os.getenv("MYSQL_ROOT_USER"),
    #         password=os.getenv("MYSQL_ROOT_PASSWORD"),
    #         charset="utf8mb4",
    #         cursorclass=pymysql.cursors.DictCursor,)
    # elif os.getenv("DB") == 'postgresql':
    if True:
        logger.info('postgresql get_connection()')
        import psycopg2
        logger.info(f'pg_url={get_settings().pg_url}')
        return psycopg2.connect(get_settings().pg_url)
    else:
        raise 'Not "mysql", not "postgresql" string was defined in env var "DB"'
        

# conn = psycopg2.connect(DSN)

# with conn:
#     with conn.cursor() as curs:
#         curs.execute(SQL1)

# with conn:
#     with conn.cursor() as curs:
#         curs.execute(SQL2)

# # leaving contexts doesn't close the connection
# conn.close()

ready = False
retry = 60
while not ready:
    try:
        conn = get_connection()
        logger.info(f'{conn=}')
        ready = True
    except Exception as e:
        logger.info(f"trying to connect to bd...\n{e}")
        time.sleep(3)
        retry -= 1
        if not retry:
            msg = "Maximum number of db connection retries exceeded"
            logger.error(msg)
            raise RuntimeError(msg)


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
                    birthday,
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
            user.birthday,
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
                WHERE first_name LIKE %s AND last_name LIKE %s
                ORDER BY id;
            """
    cursor.execute(query, (f"{first_name}%", f"{last_name}%"))
    users_dict = cursor.fetchall()
    cursor.close()
    return [UserInDB(**user_dict) for user_dict in users_dict]

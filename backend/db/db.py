# import time

# import psycopg2
# from sqlalchemy.orm import Session

# from backend.log import get_logger
# from backend.models.user import User as User_model
# from backend.schemas.user import User, UserInDB, UserToDB
# from backend.utils.config import get_settings

# logger = get_logger(__name__)


# def get_connection():
#     logger.info(f"pg_url={get_settings().pg_url}")
#     return psycopg2.connect(get_settings().pg_url)


# ready = False
# retry = 60
# while not ready:
#     try:
#         conn = get_connection()
#         logger.info(f"{conn=}")
#         ready = True
#     except Exception as e:
#         logger.info(f"trying to connect to bd...\n{e}")
#         time.sleep(3)
#         retry -= 1
#         if not retry:
#             msg = "Maximum number of db connection retries exceeded"
#             logger.error(msg)
#             raise RuntimeError(msg)


# def get_dbcursor():
#     return conn


# def is_user_exist(username: str) -> bool:
#     cursor = conn.cursor()
#     query = """ SELECT username
#                 FROM user
#                 WHERE username=%s;
#             """
#     cnt = cursor.execute(query, (username))
#     return True if cnt else False


# def insert_into_user(user: UserToDB) -> User:
#     cursor = conn.cursor()
#     query = """ INSERT INTO user (
#                     username,
#                     first_name,
#                     last_name,
#                     birthday,
#                     bio,
#                     city,
#                     country,
#                     hashed_password,
#                     disabled)
#                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
#             """
#     cursor.execute(
#         query,
#         (
#             user.username,
#             user.first_name,
#             user.last_name,
#             user.birthdate,
#             user.bio,
#             user.city,
#             user.country,
#             user.hashed_password,
#             user.disabled,
#         ),
#     )
#     conn.commit()
#     user.id = cursor.lastrowid
#     cursor.close()
#     return user


# def get_model_user(row) -> User:
#     return User(
#         id=row[0],
#         username=row[1].strip(),
#         first_name=row[2].strip(),
#         last_name=row[3].strip(),
#         birthdate=row[4],
#         bio=row[5].strip(),
#         city=row[6].strip(),
#         country=row[7].strip(),
#         disabled=row[9],
#     )


# def get_user_by_username(username: str) -> UserInDB | None:
#     cursor = conn.cursor()
#     query = """ SELECT *
#                 FROM user
#                 WHERE username=%s;
#             """
#     cursor.execute(query, (username))
#     user_dict = cursor.fetchone()
#     cursor.close()
#     return UserInDB(**user_dict) if user_dict else None


# def get_user_by_id(id: int | str, db: Session) -> UserInDB | None:
#     res = db.query(User_model).filter(User_model.id == id).first()
#     logger.info(res)
#     return res


# # def get_user_by_id(id: int | str) -> UserInDB | None:
# #     logger.debug(f'{id=}, {type(id)=}')
# #     cursor = conn.cursor()
# #     query = """ SELECT *
# #                 FROM user
# #                 WHERE id=%s;
# #             """
# #     cursor.execute(query, (int(id),))
# #     row = cursor.fetchone()
# #     logger.debug(f'get_user_by_id {id=}, {row=}')
# #     cursor.close()
# #     if row is None:
# #         return None
# #     return get_model_user(row)


# def search_user(first_name: str, last_name: str) -> User | None:
#     cursor = conn.cursor()
#     query = """ SELECT *
#                 FROM user
#                 WHERE LOWER(first_name) LIKE %s AND LOWER(last_name) LIKE %s
#                 ORDER BY id;
#             """
#     cursor.execute(query, (f"{first_name}%", f"{last_name}%"))
#     users_list = cursor.fetchall()
#     cursor.close()
#     return [get_model_user(row) for row in users_list]

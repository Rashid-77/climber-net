from backend.models.user import create_user_table_query


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute(create_user_table_query)
    cursor.close()
    conn.commit()
